from contextlib import asynccontextmanager
from google import genai
from google.genai.types import (
    LiveConnectConfig, Content, Part, Tool,
    SpeechConfig, VoiceConfig as GeminiVoiceConfig, PrebuiltVoiceConfig,
    RealtimeInputConfig, AutomaticActivityDetection,
    StartSensitivity, EndSensitivity
)
from config import (
    USE_VERTEX, GEMINI_API_KEY, GOOGLE_PROJECT, GOOGLE_LOCATION,
    GEMINI_MODEL, SYSTEM_PROMPT
)
from tools import get_tool_declarations


class GeminiSession:
    def __init__(self):
        if USE_VERTEX:
            self.client = genai.Client(
                vertexai=True,
                project=GOOGLE_PROJECT,
                location=GOOGLE_LOCATION
            )
            print(f"[Gemini] Using Vertex AI: {GOOGLE_PROJECT}/{GOOGLE_LOCATION}", flush=True)
        else:
            self.client = genai.Client(
                api_key=GEMINI_API_KEY,
                http_options={"api_version": "v1alpha"}
            )
            print("[Gemini] Using Gemini API with API key (v1alpha)", flush=True)
        self.config = self._create_config()

    def _create_config(self):
        """Create LiveConnectConfig for Gemini."""
        return LiveConnectConfig(
            system_instruction=Content(parts=[Part(text=SYSTEM_PROMPT)]),
            response_modalities=["AUDIO"],
            tools=[Tool(function_declarations=get_tool_declarations())],
            speech_config=SpeechConfig(
                voice_config=GeminiVoiceConfig(
                    prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Kore")
                )
            ),
            realtime_input_config=RealtimeInputConfig(
                automatic_activity_detection=AutomaticActivityDetection(
                    disabled=False,
                    # start_of_speech_sensitivity=StartSensitivity.START_SENSITIVITY_HIGH,
                    # end_of_speech_sensitivity=EndSensitivity.END_SENSITIVITY_HIGH,
                    prefix_padding_ms=50,
                    silence_duration_ms=100,
                )
            )
        )

    @asynccontextmanager
    async def connect(self):
        """Connect to Gemini Live API."""
        print(f"Connecting to Gemini: {GEMINI_MODEL}")
        async with self.client.aio.live.connect(
            model=GEMINI_MODEL,
            config=self.config
        ) as session:
            print("Gemini connected")
            yield session
