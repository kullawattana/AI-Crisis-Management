# AI Crisis Management System

> An AI-powered emergency response platform that ensures no victim gets a busy signal during crisis situations, while intelligently prioritizing response based on severity.

## 🎯 Overview

The Crisis Bot is an intelligent call center solution designed for disaster response scenarios (floods, fires, earthquakes). It addresses critical limitations of traditional call centers by using AI to handle unlimited concurrent calls, intelligently triage cases, and provide immediate assistance while human operators focus on decision-making and resource deployment.

### The Problem

During crises, traditional call centers face critical challenges:
- **Limited capacity**: Victims get busy signals when operators are overwhelmed
- **No prioritization**: Critical cases wait behind non-urgent ones
- **Bottlenecks**: Response depends on staff availability
- **Data gaps**: Inconsistent information collection slows rescue efforts
- **Reactivity**: No automatic follow-up when victim status changes

### The Solution

An AI-assisted call center that:
- ✅ **Eliminates busy signals** - AI handles unlimited concurrent inbound calls
- ✅ **Prioritizes by severity** - Triage system routes critical cases first
- ✅ **Augments humans** - AI collects data, humans make decisions
- ✅ **Proactively monitors** - Automated pulse checks track status changes
- ✅ **Multilingual support** - AI communicates in victim's preferred language 24/7

## 🏗️ Architecture

### System Components

```
Phone (Thailand)
     ↓ ~20ms
Twilio Edge (Singapore)
     ↓ ~5ms
FastAPI Backend (GCP asia-southeast1)
     ↓ ~5ms
Gemini Live API (Text + Audio)
     ↓
Firestore Database
     ↓
React Dashboard (Crisis Management)

Total Round-Trip: ~60ms
```

### Technology Stack

**Backend:**
- **FastAPI** - High-performance Python web framework
- **Twilio** - Voice communication and media streaming
- **Google Gemini Live API** - Real-time conversation AI with native audio
- **Firestore** - Cloud database for victim records and case tracking
- **WebSockets** - Real-time bidirectional communication

**Frontend:**
- **React 19** - UI framework
- **TypeScript** - Type-safe development
- **Vite** - Modern build tool
- **Tailwind CSS** - Utility-first styling
- **Firebase** - Authentication and real-time data
- **Lucide React** - Icon library

**Deployment:**
- **Docker** - Containerization
- **Google Cloud Run** - Serverless deployment

## 📊 Triage System

Cases are prioritized into three levels:

| Priority | SLA | Criteria | Examples |
|----------|-----|----------|----------|
| **🔴 RED** | ≤ 10 min | Life threatening, urgent medical support needed | Trapped under debris, severe bleeding, difficulty breathing, heart attack |
| **🟡 YELLOW** | ≤ 30 min | Injured or at risk, not immediately critical | Broken bone, minor bleeding, malnutrition, stable but sick |
| **🟢 GREEN** | When available | Safe, needs information or non-urgent help | Property damage, needs shelter info, status updates |

**Automatic pulse checks**: Every 1 hour since last human contact (call or callback)

## 📁 Project Structure

```
AI-Crisis-Management/
├── crisis-bot/                      # Backend application
│   ├── main.py                      # FastAPI entry point
│   ├── config.py                    # Configuration and system prompt
│   ├── routes.py                    # Twilio webhooks and WebSocket handlers
│   ├── tools.py                     # AI tools (survival guide, victim recording)
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Container configuration
│   ├── CRISIS_BOT_SPEC.md          # Business requirements and use cases
│   ├── IMPLEMENTATION.md            # Technical implementation guide
│   ├── CLAUDE.md                    # AI assistant instructions
│   │
│   ├── services/                    # Core service modules
│   │   ├── gemini_service.py        # Google Gemini Live API integration
│   │   ├── twilio_service.py        # Twilio audio bridging
│   │   └── firestore_service.py     # Database operations
│   │
│   ├── dashboard/                   # React frontend application
│   │   ├── src/
│   │   │   ├── main.tsx             # Application entry point
│   │   │   ├── App.tsx              # Main app component
│   │   │   ├── firebase.ts          # Firebase configuration
│   │   │   ├── PulseCheck.tsx       # Scheduled check-in component
│   │   │   ├── Victims.tsx          # Victim management dashboard
│   │   │   ├── Resources.tsx        # Resource allocation interface
│   │   │   └── assets/              # Static assets
│   │   ├── public/                  # Public static files
│   │   ├── package.json             # Frontend dependencies
│   │   ├── vite.config.ts           # Vite build configuration
│   │   ├── tsconfig.json            # TypeScript configuration
│   │   └── tailwind.config.js       # Tailwind CSS configuration
│   │
│   └── scripts/                     # Utility scripts
│       ├── load_test.py             # Load testing script
│       └── fix_victim_data.py       # Data cleanup utilities
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git
- Docker (optional, for containerized deployment)

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/AI-Crisis-Management.git
   cd AI-Crisis-Management/crisis-bot
   ```

2. **Create a Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your credentials:
   ```env
   # Google Gemini
   GEMINI_API_KEY=your_gemini_api_key
   
   # Twilio
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=+66xxxxxxxxx
   
   # Google Cloud / Firestore
   GOOGLE_PROJECT=your_gcp_project_id
   GOOGLE_APPLICATION_CREDENTIALS=path/to/service_account.json
   
   # Optional: Use Vertex AI instead of Gemini API
   USE_VERTEX=false
   ```

5. **Run the backend:**
   ```bash
   python main.py
   ```
   The API will start on `http://localhost:9999`

### Frontend Setup

1. **Navigate to dashboard:**
   ```bash
   cd dashboard
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```
   The dashboard will be available at `http://localhost:5173`

4. **Build for production:**
   ```bash
   npm run build
   ```

## 📡 Call Flow

### Inbound Call Handling

```
1. Victim calls crisis hotline
   ↓
2. Twilio receives call
   ↓
3. FastAPI webhook processes incoming call
   ↓
4. Establish WebSocket connection to Twilio media stream
   ↓
5. Bridge Twilio ↔ Gemini Live API
   ↓
6. AI collects emergency information:
   - Situation type (flood, fire, earthquake, etc.)
   - Number of people affected
   - Location details
   - Injuries and severity
   - Immediate needs
   - Contact phone number
   ↓
7. AI assesses severity → Assigns triage level (RED/YELLOW/GREEN)
   ↓
8. AI provides survival guidance
   ↓
9. Victim information saved to Firestore
   ↓
10. Dashboard alerts human operators
    ↓
11. Operators callback victim within SLA
```

## 🔧 API Endpoints

### Twilio Webhooks

- **POST `/incoming-call`** - Handles incoming phone calls
- **WebSocket `/media-stream`** - Real-time audio streaming between Twilio and AI

### Dashboard API (Firebase)

- **Real-time listeners** on Firestore collections:
  - `victims` - Active victim records
  - `cases` - Case details with triage level
  - `pulse_checks` - Scheduled follow-ups

## 🧠 AI System Prompt

The AI assistant is configured to:

1. **Identify language** - Starts in English to detect caller's preferred language
2. **Collect critical information** - Structured data for emergency response
3. **Assess severity** - Assigns triage priority (RED/YELLOW/GREEN)
4. **Record victim data** - Calls `record_victim_info` function to save case
5. **Provide guidance** - Uses `get_survival_guide` function for immediate assistance
6. **Confirm information** - Ensures accuracy and reassures caller
7. **Support multiple languages** - Responds in caller's language

## 📊 Dashboard Features

### Victims Dashboard
- View all reported cases with real-time status
- Filter by triage priority level
- Search by victim name or location
- Victim location map visualization

### Pulse Check Management
- Schedule automatic follow-up calls
- View pulse check history
- Manual callback interface
- Status update tracking

### Resources Interface
- Allocate emergency resources to cases
- Track response team assignments
- Monitor resource availability

## 🐳 Docker Deployment

Build and run the application in a container:

```bash
# Build Docker image
docker build -t crisis-bot:latest .

# Run container
docker run -p 9999:9999 \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  -e TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID \
  -e TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN \
  -e GOOGLE_PROJECT=$GOOGLE_PROJECT \
  crisis-bot:latest
```

## ⚙️ Configuration

Key configuration options in [config.py](crisis-bot/config.py):

- **GEMINI_MODEL** - AI model selection (API vs. Vertex AI)
- **SYSTEM_PROMPT** - AI assistant behavior and instructions
- **GOOGLE_LOCATION** - Cloud region (asia-southeast1 for low latency)
- **USE_VERTEX** - Toggle between Gemini API and Vertex AI

## 📈 Performance Metrics

- **Call acceptance**: Unlimited concurrent calls (no busy signals)
- **Response latency**: ~60ms round-trip (phone → Gemini → phone)
- **Triage accuracy**: Based on structured information collection
- **Human callback SLA**: RED ≤ 10 min, YELLOW ≤ 30 min

## 🔐 Security Considerations

- **API Keys**: Store in environment variables, never in code
- **Firestore Rules**: Configure authentication in `firestore.rules`
- **Rate Limiting**: Implement call rate limits to prevent abuse
- **Data Privacy**: Comply with local data protection regulations

## 📝 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `GOOGLE_PROJECT` | GCP project ID | `bbl-mit-hack-2025` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON | `./credentials.json` |
| `TWILIO_ACCOUNT_SID` | Twilio account ID | `AC...` |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | `your_token` |
| `TWILIO_PHONE_NUMBER` | Crisis hotline phone number | `+66xxxxxxxxx` |
| `USE_VERTEX` | Use Vertex AI instead of Gemini API | `false` |

## 🧪 Testing

### Load Testing

Run the load test script to simulate multiple concurrent calls:

```bash
python scripts/load_test.py
```

### Manual Testing

1. Call the crisis hotline number configured in Twilio
2. Respond to AI questions
3. Check dashboard for case appearance
4. Verify Firestore database for saved victim data

## 📚 Documentation

- [CRISIS_BOT_SPEC.md](crisis-bot/CRISIS_BOT_SPEC.md) - Business requirements and use cases
- [IMPLEMENTATION.md](crisis-bot/IMPLEMENTATION.md) - Technical implementation details
- [CLAUDE.md](crisis-bot/CLAUDE.md) - AI assistant instructions

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add new feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Open a pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Team

Built for emergency response during crisis situations in Thailand and Southeast Asia.

---

**Note**: This system is designed for emergency use. Ensure proper testing, compliance with local regulations, and integration with existing emergency response infrastructure before deployment.
