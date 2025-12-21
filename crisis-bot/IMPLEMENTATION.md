# Crisis Bot Implementation Guide

> Implementation details derived from reference projects (call-bot, voicebot) and deployment analysis.

---

## 1. Architecture Overview

### Data Flow

```
Phone (Thailand)
     │
     ▼ ~20ms
Twilio Edge (Singapore)
     │
     ▼ ~5ms
FastAPI (GCP asia-southeast1)
     │
     ▼ ~5ms
Gemini Live API (asia-southeast1)
     │
     ▼ ~5ms
FastAPI
     │
     ▼ ~5ms
Twilio Edge
     │
     ▼ ~20ms
Phone

Total Round-Trip: ~60ms
```

### Deployment Decisions

| Component | Choice | Region | Reason |
|-----------|--------|--------|--------|
| Twilio Account | Australia (AU1) | - | Closer API, Singapore edge for media |
| Twilio Number | Thai Mobile (+66 97 xxx) | - | $22/month, works from any phone |
| FastAPI | GCP Cloud Run | asia-southeast1 (Singapore) | Same region as Gemini, low latency |
| Gemini Live | Vertex AI | asia-southeast1 (Singapore) | Confirmed available |
| Database | Firestore | asia-southeast1 | Same region |

---

## 2. Project Structure

Based on call-bot's simplicity (not voicebot's complexity):

```
crisis-bot/
├── main.py                 # FastAPI entry (~10 lines)
├── config.py               # All config (~50 lines)
├── routes.py               # Twilio webhooks + WebSocket (~100 lines)
├── tools.py                # Survival guide + record_victim (~80 lines)
├── services/
│   ├── gemini_service.py   # Gemini Live connection (~40 lines)
│   ├── twilio_service.py   # Audio bridging (~60 lines)
│   └── firestore_service.py # Simple CRUD (~50 lines)
├── requirements.txt
├── Dockerfile
└── cloudbuild.yaml         # GCP Cloud Run deployment

Total: ~7 files, ~400 lines
```

---

## 3. Reference Project Patterns

### From call-bot (USE)

**Twilio Integration Pattern:**
```python
# routes.py - Incoming call webhook
@router.post("/incoming-call")
async def handle_incoming_call(request: Request):
    response = VoiceResponse()
    connect = Connect()
    connect.stream(url=f'wss://{request.url.hostname}/media-stream')
    response.append(connect)
    return HTMLResponse(str(response), media_type="application/xml")

# routes.py - WebSocket media stream
@router.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    await websocket.accept()
    # Bridge Twilio <-> AI
    await asyncio.gather(
        receive_from_twilio(websocket, ai_session),
        receive_from_ai(ai_session, websocket)
    )
```

**Twilio Event Handling:**
```python
# From call-bot/services/websocket_manager.py
async for message in websocket.iter_text():
    data = json.loads(message)

    if data['event'] == 'start':
        stream_sid = data['start']['streamSid']

    elif data['event'] == 'media':
        audio = data['media']['payload']  # base64 mulaw
        await forward_to_ai(audio)

    elif data['event'] == 'mark':
        # Timestamp marker for audio sync
        pass
```

**Tool Parser Pattern:**
```python
# From call-bot/tools/tool_parser.py
# Auto-converts Python function to OpenAI/Gemini tool schema
def tool_parser(func):
    signature = inspect.signature(func)
    docstring = func.__doc__

    # Handle Literal types for enums
    if get_origin(param_type) is Literal:
        param_options = get_args(param_type)
        param_info = {
            "type": "string",
            "enum": list(param_options)
        }

    return function_schema
```

### From voicebot (USE)

**Gemini Live Connection:**
```python
# From voicebot/src/agent/voice_bot.py
from google import genai

class VoiceBot:
    def __init__(self, config):
        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY"),
            http_options={"api_version": "v1alpha"}
        )

    @asynccontextmanager
    async def connect(self):
        async with self.client.aio.live.connect(
            model="gemini-live-2.5-flash-preview",
            config=self.agent_config
        ) as session:
            yield session
```

**Gemini Config with Tools:**
```python
# From voicebot/src/agent/config.py
from google.genai.types import (
    LiveConnectConfig, Content, Part,
    Tool, FunctionDeclaration,
    SpeechConfig, VoiceConfig, PrebuiltVoiceConfig
)

def create_config(tools_map):
    # Convert functions to FunctionDeclarations
    declarations = []
    for func_name, func in tools_map.items():
        sig = inspect.signature(func)
        parameters = {"type": "object", "properties": {}, "required": []}

        for param_name, param in sig.parameters.items():
            if get_origin(param.annotation) is Literal:
                # Handle Literal enum types
                parameters["properties"][param_name] = {
                    "type": "string",
                    "enum": list(get_args(param.annotation))
                }

        declarations.append(FunctionDeclaration(
            name=func_name,
            description=func.__doc__,
            parameters=parameters
        ))

    return LiveConnectConfig(
        system_instruction=Content(parts=[Part(text=SYSTEM_PROMPT)]),
        response_modalities=["AUDIO"],
        tools=[Tool(function_declarations=declarations)],
        speech_config=SpeechConfig(
            language_code="th-TH",
            voice_config=VoiceConfig(
                prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Kore")
            )
        )
    )
```

**Audio Config:**
```python
# From voicebot/src/agent/config.py
class AudioConfig:
    GEMINI_RECV_RATE = 16000   # Input to Gemini
    GEMINI_SEND_RATE = 24000   # Output from Gemini
    WS_CHANNELS = 1            # Mono
    WS_CHUNK_SIZE = 4096
```

### NOT Using (Too Complex)

- voicebot's multi-company system (CompanyManager, profile.yaml)
- voicebot's threading/queue system (VoiceSocketManager)
- voicebot's customer info extraction (CustInfoExtractor)
- call-bot's Google Sheets integration
- call-bot's authenticated tools system

---

## 4. Implementation Details

### 4.1 main.py

```python
from fastapi import FastAPI
from routes import router
import uvicorn

app = FastAPI(title="Crisis Bot")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### 4.2 config.py

```python
import os
from google import genai
from google.genai.types import (
    LiveConnectConfig, Content, Part, Tool, FunctionDeclaration,
    SpeechConfig, VoiceConfig as GeminiVoiceConfig, PrebuiltVoiceConfig
)

# Environment
GOOGLE_PROJECT = os.getenv("GOOGLE_PROJECT")
GOOGLE_LOCATION = "asia-southeast1"  # Singapore

# Gemini
GEMINI_MODEL = "gemini-live-2.5-flash-preview"

SYSTEM_PROMPT = """
You are an AI assistant for emergency calls in Thailand. Your role is to:

1. Stay calm and reassuring
2. Collect critical information:
   - What is your situation? (flood, fire, earthquake, accident, medical)
   - How many people need help?
   - What is your location? (address, landmarks)
   - Is anyone injured? Describe injuries.
   - What immediate help do you need?
   - What phone number can we reach you at?

3. Assess severity:
   - RED: Life threatening, needs urgent medical support NOW
   - YELLOW: Injured/at risk but not immediately life threatening
   - GREEN: Safe, needs information or non-urgent help

4. After collecting info, call record_victim_info function
5. Provide survival guidance using get_survival_guide function
6. Confirm information back to caller

Speak in Thai. Be concise - this is phone support.
System is always available for any emergency.
"""

def create_gemini_client():
    """Create Gemini client for Vertex AI in Singapore."""
    return genai.Client(
        vertexai=True,
        project=GOOGLE_PROJECT,
        location=GOOGLE_LOCATION
    )

def create_gemini_config(tool_declarations: list[FunctionDeclaration]):
    """Create LiveConnectConfig for Gemini."""
    return LiveConnectConfig(
        system_instruction=Content(parts=[Part(text=SYSTEM_PROMPT)]),
        response_modalities=["AUDIO"],
        input_audio_transcription={},
        output_audio_transcription={},
        tools=[Tool(function_declarations=tool_declarations)],
        speech_config=SpeechConfig(
            language_code="th-TH",
            voice_config=GeminiVoiceConfig(
                prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Kore")
            )
        )
    )
```

### 4.3 tools.py

```python
from typing import Literal
import inspect
from google.genai.types import FunctionDeclaration
from services.firestore_service import create_victim

# Hardcoded survival guides (as per spec)
SURVIVAL_GUIDES = {
    "fire": """
ไฟไหม้:
- หมอบต่ำ ควันลอยขึ้น
- หาทางออกใกล้สุด อย่าใช้ลิฟต์
- ปิดจมูกด้วยผ้าเปียก
- ถ้าประตูร้อน อย่าเปิด หาทางอื่น
- ไฟติดเสื้อผ้า ให้หยุด ล้ม กลิ้ง
""",
    "flood": """
น้ำท่วม:
- อย่าเดินหรือว่ายในน้ำท่วม
- ขึ้นที่สูงทันที
- อย่าขับรถผ่านน้ำท่วม
- เก็บน้ำดื่มสะอาด
- หลีกเลี่ยงอุปกรณ์ไฟฟ้า
""",
    "earthquake": """
แผ่นดินไหว:
- หมอบ หลบ เกาะ
- หลีกเลี่ยงหน้าต่างและผนังด้านนอก
- ในอาคาร อยู่ในอาคารจนหยุดสั่น
- นอกอาคาร ไปที่โล่ง ห่างจากอาคาร
- เตรียมรับอาฟเตอร์ช็อก
""",
    "medical": """
เหตุฉุกเฉินทางการแพทย์:
- ตั้งสติ ประเมินสถานการณ์
- มีเลือดออก กดแผลด้วยผ้าสะอาด
- อย่าเคลื่อนย้ายผู้บาดเจ็บ ยกเว้นอันตราย
- ให้ผู้บาดเจ็บอบอุ่น
- รอคำแนะนำเพิ่มเติม
""",
}

def get_survival_guide(
    situation_type: Literal["fire", "flood", "earthquake", "medical"]
) -> str:
    """
    Get survival instructions for the situation type.
    Call this after identifying the emergency type to provide guidance.
    """
    return SURVIVAL_GUIDES.get(situation_type, "ตั้งสติ ความช่วยเหลือกำลังมา")

def record_victim_info(
    situation_type: str,
    victim_count: int,
    location: str,
    injuries: str,
    help_needed: str,
    phone_number: str,
    priority: Literal["RED", "YELLOW", "GREEN"],
    priority_reason: str,
) -> str:
    """
    Record victim information to database after collecting all details.
    Call this when you have gathered: situation, location, injuries, victim count, and assessed priority.
    """
    victim_id = create_victim({
        'situation_type': situation_type,
        'victim_count': victim_count,
        'location': location,
        'injuries': injuries,
        'help_needed': help_needed,
        'phone_number': phone_number,
        'priority': priority,
        'priority_reason': priority_reason,
    })
    return f"บันทึกแล้ว หมายเลขเคส: {victim_id} ระดับความเร่งด่วน: {priority}"

# Tool registry
TOOL_MAP = {
    "get_survival_guide": get_survival_guide,
    "record_victim_info": record_victim_info,
}

def get_tool_declarations() -> list[FunctionDeclaration]:
    """Convert Python functions to Gemini FunctionDeclarations."""
    from typing import get_origin, get_args

    declarations = []
    for func_name, func in TOOL_MAP.items():
        sig = inspect.signature(func)
        parameters = {"type": "object", "properties": {}, "required": []}

        for param_name, param in sig.parameters.items():
            annotation = param.annotation

            if get_origin(annotation) is Literal:
                # Enum type
                parameters["properties"][param_name] = {
                    "type": "string",
                    "enum": list(get_args(annotation))
                }
            elif annotation == int:
                parameters["properties"][param_name] = {"type": "integer"}
            else:
                parameters["properties"][param_name] = {"type": "string"}

            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)

        declarations.append(FunctionDeclaration(
            name=func_name,
            description=func.__doc__ or f"Execute {func_name}",
            parameters=parameters
        ))

    return declarations

def execute_tool(name: str, args: dict) -> str:
    """Execute a tool by name with given arguments."""
    if name in TOOL_MAP:
        return TOOL_MAP[name](**args)
    return f"Unknown tool: {name}"
```

### 4.4 services/gemini_service.py

```python
from contextlib import asynccontextmanager
from config import create_gemini_client, create_gemini_config, GEMINI_MODEL
from tools import get_tool_declarations

class GeminiSession:
    def __init__(self):
        self.client = create_gemini_client()
        self.config = create_gemini_config(get_tool_declarations())

    @asynccontextmanager
    async def connect(self):
        """Connect to Gemini Live API."""
        async with self.client.aio.live.connect(
            model=GEMINI_MODEL,
            config=self.config
        ) as session:
            yield session
```

### 4.5 services/twilio_service.py

```python
import json
import base64
from fastapi import WebSocket
from tools import execute_tool

async def receive_from_twilio(twilio_ws: WebSocket, gemini_session, state: dict):
    """Forward Twilio audio to Gemini."""
    async for message in twilio_ws.iter_text():
        data = json.loads(message)

        if data['event'] == 'start':
            state['stream_sid'] = data['start']['streamSid']
            print(f"Stream started: {state['stream_sid']}")

        elif data['event'] == 'media':
            # Twilio sends base64 mulaw audio
            # Note: May need conversion to PCM16 for Gemini
            audio_payload = data['media']['payload']
            audio_bytes = base64.b64decode(audio_payload)
            await gemini_session.send(input=audio_bytes)

        elif data['event'] == 'stop':
            print("Stream stopped")
            break

async def receive_from_gemini(gemini_session, twilio_ws: WebSocket, state: dict):
    """Forward Gemini audio to Twilio and handle tool calls."""
    async for response in gemini_session.receive():
        # Handle audio response
        if hasattr(response, 'data') and response.data:
            audio_b64 = base64.b64encode(response.data).decode('utf-8')
            await twilio_ws.send_json({
                "event": "media",
                "streamSid": state.get('stream_sid'),
                "media": {"payload": audio_b64}
            })

        # Handle tool calls
        if hasattr(response, 'tool_call') and response.tool_call:
            tool_name = response.tool_call.name
            tool_args = json.loads(response.tool_call.args)

            print(f"Tool call: {tool_name}({tool_args})")
            result = execute_tool(tool_name, tool_args)

            # Send tool result back to Gemini
            await gemini_session.send(tool_response={
                "name": tool_name,
                "response": result
            })

        # Handle transcription (for logging)
        if hasattr(response, 'server_content'):
            if response.server_content.input_transcription:
                print(f"User: {response.server_content.input_transcription.text}")
            if response.server_content.output_transcription:
                print(f"AI: {response.server_content.output_transcription.text}")
```

### 4.6 services/firestore_service.py

```python
from google.cloud import firestore
from datetime import datetime, timedelta

db = firestore.Client()

def create_victim(data: dict) -> str:
    """Create victim document, return ID."""
    now = datetime.now()
    priority = data.get('priority', 'GREEN')

    doc = {
        'phoneNumber': data.get('phone_number', ''),
        'primaryLanguage': 'th',
        'location': {'text': data.get('location', '')},
        'victimCount': data.get('victim_count', 1),
        'condition': data.get('situation_type', ''),
        'injuryDetails': data.get('injuries', ''),
        'helpNeeded': data.get('help_needed', ''),
        'situationType': data.get('situation_type', 'unknown'),
        'priority': priority,
        'priorityReason': data.get('priority_reason', ''),
        'status': 'pending',
        'createdAt': now,
        'updatedAt': now,
        'lastContactAt': now,
        'nextPulseAt': now + timedelta(hours=1),
        'callbackDueAt': _calculate_callback_due(priority),
        'aiTranscript': '',
        'notes': '',
        'callHistory': [],
    }

    _, ref = db.collection('victims').add(doc)
    return ref.id

def _calculate_callback_due(priority: str) -> datetime:
    """Calculate callback deadline based on priority."""
    now = datetime.now()
    if priority == 'RED':
        return now + timedelta(minutes=10)
    elif priority == 'YELLOW':
        return now + timedelta(minutes=30)
    return now + timedelta(hours=24)

def add_call_to_history(victim_id: str, call_data: dict):
    """Append call record to victim's callHistory."""
    ref = db.collection('victims').document(victim_id)
    ref.update({
        'callHistory': firestore.ArrayUnion([call_data]),
        'lastContactAt': datetime.now(),
        'updatedAt': datetime.now(),
    })
```

### 4.7 routes.py

```python
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

    # Use wss:// for secure WebSocket
    host = request.url.hostname
    connect.stream(url=f'wss://{host}/media-stream')

    response.append(connect)
    return HTMLResponse(str(response), media_type="application/xml")

@router.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """Bridge Twilio audio <-> Gemini Live."""
    await websocket.accept()
    print("WebSocket connected")

    state = {'stream_sid': None}
    gemini = GeminiSession()

    try:
        async with gemini.connect() as session:
            await asyncio.gather(
                receive_from_twilio(websocket, session, state),
                receive_from_gemini(session, websocket, state),
            )
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("WebSocket disconnected")
```

---

## 5. Audio Format Considerations

### Twilio Audio Format
- Codec: **mulaw** (G.711 μ-law)
- Sample rate: **8000 Hz**
- Channels: **Mono**
- Encoding: **base64**

### Gemini Audio Format
- Input: **PCM16**, **16000 Hz**, Mono
- Output: **PCM16**, **24000 Hz**, Mono

### Conversion May Be Needed

```python
# If Gemini doesn't accept mulaw directly, convert:
import audioop

def mulaw_to_pcm16(mulaw_bytes: bytes) -> bytes:
    """Convert mulaw 8kHz to PCM16 16kHz."""
    # Decode mulaw to linear PCM
    pcm_8k = audioop.ulaw2lin(mulaw_bytes, 2)
    # Resample 8kHz -> 16kHz
    pcm_16k, _ = audioop.ratecv(pcm_8k, 2, 1, 8000, 16000, None)
    return pcm_16k

def pcm16_to_mulaw(pcm_bytes: bytes, from_rate: int = 24000) -> bytes:
    """Convert PCM16 24kHz to mulaw 8kHz."""
    # Resample to 8kHz
    pcm_8k, _ = audioop.ratecv(pcm_bytes, 2, 1, from_rate, 8000, None)
    # Encode to mulaw
    mulaw = audioop.lin2ulaw(pcm_8k, 2)
    return mulaw
```

**Note:** Test first without conversion - Gemini may handle mulaw directly.

---

## 6. Deployment

### requirements.txt

```
fastapi==0.115.0
uvicorn==0.32.0
websockets==13.0
twilio==9.3.0
google-genai==0.3.0
google-cloud-firestore==2.19.0
python-dotenv==1.0.0
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Deploy to Cloud Run

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com

# Deploy
gcloud run deploy crisis-bot \
  --source . \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_PROJECT=YOUR_PROJECT_ID
```

### Twilio Configuration

1. Buy Thai mobile number from **Australia (AU1)** region
2. Configure webhook:
   - Voice webhook: `https://YOUR_CLOUD_RUN_URL/incoming-call`
   - Method: POST

---

## 7. Testing

### Local Testing

```bash
# Install ngrok for local tunnel
ngrok http 8080

# Run locally
python main.py

# Configure Twilio webhook to ngrok URL
```

### Test Checklist

1. [ ] Twilio webhook receives call
2. [ ] WebSocket connects
3. [ ] Audio flows Twilio -> Gemini
4. [ ] Gemini responds with audio
5. [ ] Audio flows Gemini -> Twilio
6. [ ] Tool calls work (get_survival_guide)
7. [ ] Tool calls work (record_victim_info)
8. [ ] Firestore saves victim data
9. [ ] Thai language works correctly

---

## 8. Implementation Phases

### Phase 1: Basic Connection
- [ ] FastAPI + routes.py
- [ ] Twilio webhook returns TwiML
- [ ] WebSocket accepts connection
- [ ] Log Twilio events

### Phase 2: Gemini Integration
- [ ] GeminiSession connects
- [ ] Audio forwarding works
- [ ] Response audio plays

### Phase 3: Tools
- [ ] get_survival_guide works
- [ ] record_victim_info works
- [ ] Firestore saves data

### Phase 4: Production
- [ ] Deploy to Cloud Run
- [ ] Test with real phone calls
- [ ] Monitor latency

---

## 9. Key Differences from Reference Projects

| Aspect | call-bot | voicebot | crisis-bot |
|--------|----------|----------|------------|
| AI Provider | OpenAI Realtime | Gemini Live | Gemini Live (Vertex AI) |
| Region | US | Not specified | Singapore (asia-southeast1) |
| Framework | FastAPI | Flask | FastAPI |
| Database | Google Sheets | None | Firestore |
| Tools | Credit card auth | Company knowledge | Survival guide + triage |
| Multi-tenant | No | Yes (companies) | No |
| Complexity | Low (~600 lines) | High (~1750 lines) | Low (~400 lines) |

---

*Document Version: 1.0*
*Last Updated: December 2024*
