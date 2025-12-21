import json
import base64
import audioop
from fastapi import WebSocket
from google.genai.types import Blob
from tools import execute_tool


class AudioConverter:
    """Maintains state for streaming audio conversion."""
    def __init__(self):
        self.upsample_state = None  # 8kHz -> 16kHz state
        self.downsample_state = None  # 24kHz -> 8kHz state

    def mulaw_to_pcm(self, mulaw_data: bytes) -> bytes:
        """Convert mulaw 8kHz to PCM 16-bit 16kHz."""
        # Decode mulaw to PCM 16-bit
        pcm_8k = audioop.ulaw2lin(mulaw_data, 2)
        # Resample 8kHz to 16kHz (Gemini expects 16kHz) - maintain state
        pcm_16k, self.upsample_state = audioop.ratecv(pcm_8k, 2, 1, 8000, 16000, self.upsample_state)
        return pcm_16k

    def pcm_to_mulaw(self, pcm_data: bytes) -> bytes:
        """Convert PCM 16-bit 24kHz to mulaw 8kHz."""
        # Resample 24kHz to 8kHz - maintain state
        pcm_8k, self.downsample_state = audioop.ratecv(pcm_data, 2, 1, 24000, 8000, self.downsample_state)
        # Encode to mulaw
        mulaw = audioop.lin2ulaw(pcm_8k, 2)
        return mulaw


async def receive_from_twilio(twilio_ws: WebSocket, gemini_session, state: dict):
    """Forward Twilio audio to Gemini."""
    call_id = state.get('call_id', '?')
    print(f"[{call_id}] Twilio: Starting receive loop", flush=True)
    audio_count = 0
    send_count = 0
    converter = AudioConverter()
    state['converter'] = converter  # Share converter for response handling
    audio_buffer = bytearray()
    CHUNK_SIZE = 4096  # Buffer size matching voicebot (128ms at 16kHz)

    try:
        async for message in twilio_ws.iter_text():
            data = json.loads(message)

            if data['event'] == 'start':
                state['stream_sid'] = data['start']['streamSid']
                print(f"[{call_id}] Twilio: Stream started (sid: {state['stream_sid'][-12:]})", flush=True)
                # Send kickoff to make Gemini start talking
                kickoff = "Greet the caller and ask how you can help with their emergency."
                await gemini_session.send_realtime_input(text=kickoff)
                print(f"[{call_id}] Twilio: Sent kickoff", flush=True)

            elif data['event'] == 'media':
                audio_payload = data['media']['payload']
                mulaw_bytes = base64.b64decode(audio_payload)
                pcm_bytes = converter.mulaw_to_pcm(mulaw_bytes)
                audio_buffer.extend(pcm_bytes)
                audio_count += 1

                # Send when buffer reaches chunk size
                while len(audio_buffer) >= CHUNK_SIZE:
                    chunk = bytes(audio_buffer[:CHUNK_SIZE])
                    audio_buffer = audio_buffer[CHUNK_SIZE:]
                    await gemini_session.send_realtime_input(media=Blob(data=chunk, mime_type="audio/pcm;rate=16000"))
                    send_count += 1
                    if send_count == 1:
                        print(f"[{call_id}] Twilio: First chunk {len(chunk)}B", flush=True)
                    if send_count % 50 == 0:
                        print(f"[{call_id}] Twilio: Sent {send_count} chunks", flush=True)

            elif data['event'] == 'stop':
                print(f"[{call_id}] Twilio: Stream stopped", flush=True)
                break

    except Exception as e:
        print(f"[{call_id}] Twilio: Receive error: {e}", flush=True)
    print(f"[{call_id}] Twilio: Loop ended, sent {audio_count} total chunks", flush=True)


async def receive_from_gemini(gemini_session, twilio_ws: WebSocket, state: dict):
    """Forward Gemini audio to Twilio and handle tool calls."""
    from google.genai.types import FunctionResponse
    call_id = state.get('call_id', '?')
    print(f"[{call_id}] Gemini: Starting receive loop", flush=True)
    response_count = 0
    audio_chunks_sent = 0
    try:
        # Keep receiving - session.receive() may end after each turn
        while True:
            async for response in gemini_session.receive():
                response_count += 1

                # Handle audio from model_turn
                if hasattr(response, 'server_content') and response.server_content:
                    sc = response.server_content

                    # Check for turn_complete
                    if hasattr(sc, 'turn_complete') and sc.turn_complete:
                        print(f"[{call_id}] Gemini: Turn complete (resp #{response_count})", flush=True)

                    # Check for interrupted
                    if hasattr(sc, 'interrupted') and sc.interrupted:
                        print(f"[{call_id}] Gemini: Interrupted", flush=True)

                    if hasattr(sc, 'model_turn') and sc.model_turn:
                        for part in sc.model_turn.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                pcm_data = part.inline_data.data
                                converter = state.get('converter', AudioConverter())
                                mulaw_bytes = converter.pcm_to_mulaw(pcm_data)
                                audio_b64 = base64.b64encode(mulaw_bytes).decode('utf-8')
                                await twilio_ws.send_json({
                                    "event": "media",
                                    "streamSid": state.get('stream_sid'),
                                    "media": {"payload": audio_b64}
                                })
                                audio_chunks_sent += 1
                                if audio_chunks_sent == 1:
                                    print(f"[{call_id}] Gemini: First audio chunk sent", flush=True)
                                if audio_chunks_sent % 100 == 0:
                                    print(f"[{call_id}] Gemini: Sent {audio_chunks_sent} audio chunks", flush=True)

                    # Handle transcription (for logging)
                    if hasattr(sc, 'input_transcription') and sc.input_transcription:
                        text = sc.input_transcription.text if hasattr(sc.input_transcription, 'text') else str(sc.input_transcription)
                        print(f"[{call_id}] User: {text}", flush=True)
                    if hasattr(sc, 'output_transcription') and sc.output_transcription:
                        text = sc.output_transcription.text if hasattr(sc.output_transcription, 'text') else str(sc.output_transcription)
                        print(f"[{call_id}] AI: {text}", flush=True)

                # Handle tool calls
                if hasattr(response, 'tool_call') and response.tool_call:
                    print(f"[{call_id}] Tool call received", flush=True)
                    tool_responses = []
                    for function_call in response.tool_call.function_calls:
                        print(f"[{call_id}] Tool: {function_call.name}({function_call.args})", flush=True)
                        result = execute_tool(function_call.name, function_call.args)
                        print(f"[{call_id}] Tool result: {result}", flush=True)
                        tool_responses.append(FunctionResponse(
                            id=function_call.id,
                            name=function_call.name,
                            response={"result": result}
                        ))
                    await gemini_session.send_tool_response(function_responses=tool_responses)

    except Exception as e:
        from starlette.websockets import WebSocketDisconnect
        if isinstance(e, WebSocketDisconnect):
            print(f"[{call_id}] Gemini: Twilio disconnected (user hung up)", flush=True)
        else:
            import traceback
            print(f"[{call_id}] Gemini: Error: {e}", flush=True)
            print(f"[{call_id}] Gemini: {traceback.format_exc()}", flush=True)

    print(f"[{call_id}] Gemini: Loop ended. Responses: {response_count}, audio sent: {audio_chunks_sent}", flush=True)
