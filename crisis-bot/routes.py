from fastapi import APIRouter, WebSocket, Request
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Connect
from services.gemini_service import GeminiSession
from services.twilio_service import receive_from_twilio, receive_from_gemini
import asyncio

router = APIRouter()


@router.get("/")
async def health():
    return {"status": "ok", "service": "crisis-bot"}


@router.post("/incoming-call")
async def incoming_call(request: Request):
    """Twilio webhook - return TwiML to connect media stream."""
    response = VoiceResponse()
    connect = Connect()

    host = request.url.hostname
    connect.stream(url=f'wss://{host}/media-stream')

    response.append(connect)
    return HTMLResponse(str(response), media_type="application/xml")


@router.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """Bridge Twilio audio <-> Gemini Live."""
    await websocket.accept()

    # Generate a short call ID for logging (will be replaced by stream_sid when available)
    import uuid
    call_id = uuid.uuid4().hex[:8]
    state = {'stream_sid': None, 'call_id': call_id}

    print(f"[{call_id}] WebSocket connected", flush=True)
    gemini = GeminiSession()

    try:
        print(f"[{call_id}] Connecting to Gemini...", flush=True)
        async with gemini.connect() as session:
            print(f"[{call_id}] Gemini connected, starting tasks", flush=True)
            await asyncio.gather(
                receive_from_twilio(websocket, session, state),
                receive_from_gemini(session, websocket, state),
            )
    except Exception as e:
        print(f"[{call_id}] Error: {e}", flush=True)
    finally:
        print(f"[{call_id}] WebSocket disconnected", flush=True)
