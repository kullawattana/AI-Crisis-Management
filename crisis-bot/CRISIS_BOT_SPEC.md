# AI Crisis Communication System

> An AI-powered call center solution that ensures no victim gets a busy signal during crisis situations, while intelligently prioritizing response based on severity.

---

# PART 1: BUSINESS & USE CASE

---

## 1.1 Problem Statement

During crisis situations (floods, fires, earthquakes), traditional call centers face critical limitations:

| Problem | Impact |
|---------|--------|
| Limited concurrent calls | Victims get busy signals |
| First-come-first-served | Critical cases wait behind non-urgent ones |
| Human operator bottleneck | Response time depends on staff availability |
| Inconsistent data collection | Information gaps delay rescue efforts |
| No proactive follow-up | Victim status changes go unnoticed |

**Core Insight**: During crises, internet becomes unreliable. Phone calls remain the primary communication channel, but traditional call centers cannot scale.

---

## 1.2 Proposed Solution

An AI-assisted call center that:

1. **Eliminates busy signals** - AI handles unlimited concurrent inbound calls
2. **Prioritizes by severity** - Triage system ensures critical cases get fastest response
3. **Augments humans** - AI collects data, humans make decisions and take action
4. **Proactively monitors** - Automated pulse checks track victim status changes
5. **Supports multiple languages** - AI communicates in victim's preferred language 24/7

### Key Principle: AI Extends Human Capacity

```
AI Role:                          Human Role:
├── Answer all calls              ├── Review triaged cases
├── Collect structured data       ├── Callback within SLA
├── Assess severity               ├── Verify information
├── Provide survival guidance     ├── Authorize resource deployment
└── Conduct pulse checks          └── Handle complex situations
```

---

## 1.3 Triage System

### Priority Levels

| Priority | SLA | Criteria | Examples |
|----------|-----|----------|----------|
| **RED** | Human callback ≤ 10 min | Life threatening, needs urgent medical support | Trapped under debris, severe bleeding, difficulty breathing, heart attack symptoms |
| **YELLOW** | Human callback ≤ 30 min | Injured or at risk, not immediately life threatening | Broken bone, minor bleeding, starvation >1 day, sick but stable |
| **GREEN** | Human callback when available | Safe, needs information or non-urgent assistance | Property damage only, needs shelter information, requesting status updates |

**All cases**: AI pulse check every 1 hour since last contact (human call or AI call)

### Triage Decision Flow

```
Incoming Call
     │
     ▼
┌─────────────────────────────┐
│ Life threatening?           │
│ Needs urgent medical NOW?   │
└─────────────────────────────┘
        │
    ┌───┴───┐
   YES      NO
    │        │
    ▼        ▼
  [RED]   ┌─────────────────────────────┐
  10 min  │ Bleeding? Broken bone?      │
          │ Starvation >1 day?          │
          │ Sick but not critical?      │
          └─────────────────────────────┘
                    │
                ┌───┴───┐
               YES      NO
                │        │
                ▼        ▼
            [YELLOW]  [GREEN]
             30 min   when avail

All cases: AI pulse check every 1 hr since last contact
```

---

## 1.4 Call Flow

### Inbound Call (Victim → System)

```
1. Victim calls crisis hotline
2. AI answers immediately (no busy signal)
3. AI collects information:
   - Primary language (auto-detected)
   - Number of victims
   - Location (address, landmarks)
   - Injuries/conditions
   - Immediate help needed
   - Contact phone number
4. AI assesses severity → RED/YELLOW/GREEN
5. AI provides relevant survival guidance
6. Case enters human callback queue (prioritized)
7. Human calls back within SLA
```

### Outbound Pulse Check (System → Victim)

```
For ALL cases, every 1 hour since last contact (human or AI call):

1. AI calls victim
2. "How are you now? Any changes in your situation?"
3. Assess response:
   - Worse → Escalate priority (GREEN→YELLOW, YELLOW→RED)
   - Same → Log, schedule next check in 1 hour
   - Resolved → Close case
   - No answer → Flag for human review
```

### Human Callback Flow

```
1. Human operator sees prioritized queue
2. RED cases always at top
3. Human calls victim to:
   - Verify collected information
   - Assess actual situation
   - Authorize resource deployment
   - Provide additional guidance
4. Update case status in system
```

---

## 1.5 Survival Guidance

AI provides predetermined survival instructions based on crisis type. This approach:
- Ensures consistent, vetted advice
- Reduces liability (following established protocols)
- Allows AI to improvise only when no preset exists

### Preset Survival Scripts

#### Fire
- Stay low to the ground - smoke rises
- Find nearest exit, do not use elevators
- Cover nose and mouth with wet cloth
- If door is hot, do not open - find alternate exit
- Stop, drop, and roll if clothes catch fire

#### Flood
- Do not walk or swim through floodwater
- Move to higher ground immediately
- Do not drive through flooded roads
- Preserve clean drinking water
- Avoid contact with electrical equipment

#### Earthquake
- Drop, cover, and hold on
- Stay away from windows and exterior walls
- If indoors, stay indoors until shaking stops
- If outdoors, move to open area away from buildings
- Expect aftershocks

#### Unknown Scenario
- AI generates contextual advice
- Response logged for human review
- Added to preset database after verification

---

## 1.6 Dashboard Panels

The dashboard has 3 main tabs with a clean white/light theme:

### Cases Tab
- View all cases with priority badges (RED/YELLOW/GREEN)
- Stats cards showing count by priority
- Filter by priority, toggle closed cases
- Case list sorted by priority then time
- Detail panel with:
  - Ticket number (C + date + 6 digits)
  - Status badges (PENDING/CONTACTED/RESOLVED/CLOSED)
  - Language indicator
  - Callback countdown timer
  - Location, injuries, help needed
  - Assigned resources
  - Call history
  - Notes (editable)
- Quick actions: Mark Contacted, Mark Resolved, Close, Reopen
- Assign resources from dropdown

### Pulse Check Tab
- View cases due for pulse check
- Stats: Pending, Overdue, Urgent (≤15 min)
- List sorted by next pulse time
- Color-coded urgency (red=overdue, amber=urgent, purple=normal)
- Quick confirm buttons to update priority
- Schedule next pulse (+1 hour)
- Mark resolved option

### Resources Tab
- Stats: Total, Available, Deployed
- List resources by type
- Status badges (AVAILABLE/DEPLOYED/OFFLINE)
- Capacity display (available/total)
- Detail panel with contact info
- Allocations list with status
- Quick actions: Mark Available, Mark Deployed, Mark Offline, Allocate

---

## 1.7 Key Design Decisions

### Network Resilience Clarification

The system's network dependencies are different from the victim's connectivity:

```
Victim's Phone ──(cellular)──▶ Telco Tower ──(PSTN/SIP)──▶ Twilio ──(internet)──▶ Server
                                   │                              │
                              Crisis Area                   Cloud Infrastructure
                          (may be affected)                    (stable)
```

**Key insight**: Victims only need cellular signal to reach a cell tower. Once the call enters Twilio's infrastructure, it travels over reliable backbone networks. The server runs in high-availability cloud infrastructure (AWS/GCP).

Cell tower damage affects human call centers equally - this is not a unique weakness of the AI approach.

### Multi-Language Support

**Critical for crisis response**: Victims may be tourists, migrant workers, or residents who don't speak the local language. Traditional call centers struggle to staff operators for every language.

AI provides advantages over human operators:

| Scenario | Human Operator | AI Agent |
|----------|---------------|----------|
| Native language caller | Depends on staff on duty | Always available |
| Foreign language (tourist) | Unlikely to have staff | Can handle immediately |
| Migrant worker | Rarely have staff | Supports their language |
| Caller in shock/unclear | Trained humans may be better | Improving rapidly |
| 24/7 coverage | Expensive staffing | Built-in |

**Key capabilities:**
- Auto-detect victim's language from speech
- Respond in victim's preferred language
- Store primary language in victim record for human callback
- Provide survival guidance in victim's language
- Human operator sees language preference before callback

AI provides **consistent multi-language coverage 24/7** without staffing constraints. During crisis, this can be life-saving for non-native speakers.

### Human Callback Design - Not Replacement

The AI system improves human workflow through prioritization, not replacement:

```
Before (Traditional):
  1000 calls ──▶ 10 humans ──▶ FCFS queue ──▶ Busy signals + random priority

After (AI-Assisted):
  1000 calls ──▶ AI intake (all handled) ──▶ Triage DB
                                                  │
                                           ┌──────┼──────┐
                                           ▼      ▼      ▼
                                         RED   YELLOW  GREEN
                                          │      │       │
                                          ▼      ▼       ▼
                                    10 humans (same count)
                                    (work by priority: RED first, then YELLOW, then GREEN)
                                                         │
                                                         ▼
                                    All cases: AI pulse check every 1 hr since last contact
```

**Same 10 humans, but they work on highest severity first** instead of whoever called first. A RED case that called 5 minutes ago gets attention before a GREEN case that called 30 minutes ago.

The AI doesn't replace humans - it **makes the queue smarter**.

---

## 1.8 Risk Mitigations

| Risk | Mitigation Strategy |
|------|---------------------|
| **Liability for wrong advice** | Use predetermined survival scripts per scenario. AI improvises only when no preset exists. All advice logged. |
| **AI system failure** | AI is second line of defense. System failure = revert to traditional manual process. No worse than baseline. |
| **Public trust issues** | Human callback in ALL cases. AI positioned as data collector + prioritizer, not decision maker. |
| **Data privacy concerns** | Victim data not used for training. Role-based access control. Audit logs. Auto-deletion after resolution. |
| **Data correctness** | Human verification before any resource deployment. AI data treated as preliminary. |
| **Emergency services integration** | Portal access provided. Bureaucratic integration resolved outside technical solution. |

---

## 1.9 Sustainability Model

### The "Always On" Advantage

**Critical insight**: Systems that sit idle between crises become outdated and fail when needed most.

```
Idle Crisis System:                    Active Commercial System:
├── Last used: 18 months ago           ├── Used daily for commercial calls
├── Software: Outdated dependencies    ├── Software: Updated continuously
├── Bugs: Unknown until crisis         ├── Bugs: Found and fixed daily
├── Staff: Forgot how to use           ├── Staff: Uses dashboard daily
├── AI Models: Stale                   ├── AI Models: Latest capabilities
├── Scaling: Unknown capacity          ├── Scaling: Proven under daily load
└── When crisis hits: "Why broken?!"   └── When crisis hits: "Switch mode" ✓
```

### Sustainability Benefits

| Benefit | How Commercial Use Achieves It |
|---------|-------------------------------|
| **System Alive & Ready to Scale** | Daily commercial traffic keeps infrastructure warm and proves scaling capacity. When crisis hits, system is already running and can scale immediately. |
| **Always Latest AI Models** | Commercial revenue funds continuous updates. New model releases (Gemini updates, etc.) are integrated promptly because the system is actively developed. |
| **Crisis Operations Funded** | Profit from commercial operations (bank, telco, restaurant calls) pays for infrastructure and maintenance. When crisis occurs, system runs at cost - no budget scramble needed. |

### Revenue Sustains Crisis Readiness

```
Commercial Operations                    Crisis Operations
├── Daily revenue generation             ├── Runs at cost (no profit)
├── Covers infrastructure costs    ───▶  ├── Infrastructure already paid
├── Funds development team               ├── Team already trained
├── Pays for AI model updates            ├── Latest models available
└── Proves system reliability            └── Proven system deployed
```

**The commercial use isn't just monetization - it's a reliability and sustainability strategy.**

### Commercial Use Cases

#### Inbound
- Bank/Telco customer service
- Restaurant reservations
- Appointment scheduling
- General inquiries

#### Outbound
- Hospital appointment reminders
- Insurance policy sales
- Payment reminders
- Survey collection

### Crisis Mode Switch

```
Normal Operations (Daily)              Crisis Mode (When Needed)
├── Commercial calls                   ├── Crisis calls prioritized
├── Standard greeting/scripts          ├── Crisis scripts activated
├── Business hours focus               ├── 24/7 operation
└── Revenue generation                 └── Survival guidance enabled
```

Same infrastructure, same team, different configuration.

---

## 1.10 Business Model

### Pricing Structure

**Time-based billing**: Simple, transparent, aligned with costs

| Item | Rate |
|------|------|
| Customer price | $0.10 / minute |
| AI cost (Gemini) | ~$0.02-0.03 / minute |
| Telephony cost | ~$0.01 / minute |
| **Gross margin** | **~$0.06-0.07 / minute (60-70%)** |

### Revenue Examples

| Use Case | Monthly Volume | Revenue | Cost | Margin |
|----------|---------------|---------|------|--------|
| Bank call center | 10,000 min | $1,000 | ~$350 | $650 |
| Restaurant reservations | 5,000 min | $500 | ~$175 | $325 |
| Hospital reminders | 8,000 min | $800 | ~$280 | $520 |

### Crisis Operations

| Scenario | Volume | Cost | Funding |
|----------|--------|------|---------|
| Major flood (1,000 calls × 3 min) | 3,000 min | ~$105 | Government contract or subsidized |
| Building fire (100 calls × 3 min) | 300 min | ~$10.50 | Municipal budget |

---

## 1.11 Post-Crisis Features (Future)

### Damage Assessment Integration
- Link with victim database
- Photo-based damage assessment for:
  - Building damage (cracks, structural)
  - Vehicle damage
  - Property loss documentation
- Integration with insurance claims
- Support for government remedy programs

### Data Sources (To Be Resolved)
- Building crack assessment: Available
- Fire damage assessment: TBD
- Flood damage assessment: TBD
- Potential: Satellite imagery providers, insurance databases

---

## 1.12 Future Integrations

### Catastrophe Alert Systems
- Link with national disaster alert systems
- Automatic crisis mode activation
- Pre-positioned resource allocation
- Proactive outbound to affected areas

### Country-Specific Examples
- Thailand: Department of Disaster Prevention and Mitigation
- USA: FEMA Alerts
- Japan: J-Alert System
- Others: Per-country integration

---

# PART 2: TECHNICAL ARCHITECTURE

---

## 2.1 System Overview (Demo)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL LAYER                                 │
│                                                                             │
│   Victim Phone ──────▶ Telco Network ──────▶ Twilio                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              VOICE AI LAYER                                 │
│                                                                             │
│                         Gemini 2.5 Flash Live                               │
│                    (Real-time voice conversation)                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION LAYER                                 │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Triage    │  │  Survival   │  │  Outbound   │  │  Callback   │        │
│  │   Engine    │  │   Guide     │  │  Scheduler  │  │   Queue     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                     │
│                                                                             │
│                       Firebase Firestore                                    │
│                                                                             │
│             ┌─────────────────┐       ┌─────────────────┐                  │
│             │     victims     │       │    resources    │                  │
│             │   (collection)  │       │   (collection)  │                  │
│             └─────────────────┘       └─────────────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DASHBOARD LAYER                                  │
│                                                                             │
│         ┌─────────────────┐              ┌─────────────────┐               │
│         │  Victim Panel   │              │ Resource Panel  │               │
│         └─────────────────┘              └─────────────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2.2 Technology Stack (Demo)

| Layer | Technology | Notes |
|-------|------------|-------|
| **Voice AI** | Gemini 2.5 Flash Live | Real-time voice, ~$0.02-0.03/min |
| **Telephony** | Twilio | SIP trunking, phone numbers |
| **Backend** | Python / Node.js | API server |
| **Database** | Firebase Firestore | NoSQL, real-time listeners, serverless |
| **Dashboard** | React / Next.js | Web-based operator interface |
| **Hosting** | Firebase / Vercel | Simplified deployment |
| **Auth** | Skipped for demo | Future: Firebase Auth |

---

## 2.3 Firestore Collections (Demo)

For the demo, we use 2 Firestore collections with embedded data for simplicity.

### victims collection

```typescript
// Collection: victims
// Document ID: ticketNumber (e.g., C20251218560446)

interface Victim {
  // Identity
  ticketNumber: string;     // Format: C + YYYYMMDD + 6 random digits
  phoneNumber: string;
  primaryLanguage: string;  // Full name: Thai, English, Chinese, etc.

  // Location
  location: {
    text: string;
    latitude?: number;
    longitude?: number;
  };

  // Situation
  victimCount: number;
  condition: string;
  injuryDetails: string;
  helpNeeded: string;
  situationType: string;  // flood, fire, earthquake, etc.

  // Triage
  priority: 'RED' | 'YELLOW' | 'GREEN';
  priorityReason: string;

  // Status
  status: 'pending' | 'contacted' | 'resolved' | 'closed';

  // Timestamps
  createdAt: Timestamp;
  updatedAt: Timestamp;
  lastContactAt: Timestamp;
  nextPulseAt: Timestamp;
  callbackDueAt: Timestamp;

  // Metadata
  aiTranscript: string;
  notes: string;

  // Embedded call history (instead of separate call_logs table)
  callHistory: CallRecord[];
}

interface CallRecord {
  direction: 'inbound' | 'outbound';
  callType: 'initial' | 'callback' | 'pulse_check';
  startedAt: Timestamp;
  durationSec: number;
  summary: string;
  guidanceGiven: string;
  telephonyId: string;  // Twilio SID
}
```

### resources collection

```typescript
// Collection: resources
// Document ID: auto-generated

interface Resource {
  // Resource info
  type: 'ambulance' | 'rescue_team' | 'shelter' | 'medical_team' | string;
  name: string;

  // Capacity
  totalCapacity: number;
  available: number;

  // Location
  baseLocation: {
    text: string;
    latitude?: number;
    longitude?: number;
  };

  // Status
  status: 'available' | 'deployed' | 'offline';

  // Contact
  contactPhone: string;
  contactName: string;

  // Timestamps
  createdAt: Timestamp;
  updatedAt: Timestamp;

  // Embedded allocations (instead of separate resource_allocations table)
  allocations: Allocation[];
}

interface Allocation {
  victimId: string;
  allocatedAt: Timestamp;
  status: 'allocated' | 'dispatched' | 'arrived' | 'completed';
  dispatchedAt?: Timestamp;
  arrivedAt?: Timestamp;
  completedAt?: Timestamp;
  notes: string;
}
```

### Demo Simplifications

| Original Concept | Demo Approach |
|------------------|---------------|
| `call_logs` table | Embedded in `victims.callHistory` array |
| `resource_allocations` table | Embedded in `resources.allocations` array |
| `crises` table | Removed - system always available, `situationType` stored per victim |
| `users` table | Skipped - no auth for demo |
| `survival_guides` table | Hardcoded function (see section 2.5) |

### Firestore Indexes

```
// Composite indexes for common queries

// Query victims by priority (for callback queue)
victims: priority ASC, callbackDueAt ASC

// Query victims for pulse check scheduling
victims: status ASC, nextPulseAt ASC

// Query resources by availability
resources: type ASC, status ASC, available DESC
```

---

## 2.4 API Endpoints

### Call Handling

```
POST /api/calls/inbound
  - Webhook from Twilio
  - Initiates AI conversation
  - Creates victim record in Firestore

POST /api/calls/outbound
  - Trigger outbound call (pulse check or callback)
  - Body: { victimId, callType }

POST /api/calls/{callId}/complete
  - Webhook when call ends
  - Saves transcript, updates victim, appends to callHistory
```

### Victims

```
GET  /api/victims
  - List victims with filters
  - Query: priority, status, situationType

GET  /api/victims/{id}
  - Get single victim details with callHistory

PATCH /api/victims/{id}
  - Update victim (status, notes, priority override)

POST /api/victims/{id}/callback
  - Mark callback complete
  - Body: { notes, newStatus }
```

### Resources

```
GET  /api/resources
  - List all resources
  - Query: type, status, available

POST /api/resources/{id}/allocate
  - Allocate to victim
  - Body: { victimId }
  - Appends to allocations array

POST /api/resources/{id}/release
  - Release allocation
  - Body: { victimId }
```

### Dashboard

```
GET  /api/dashboard/stats
  - Current statistics
  - Counts by priority, SLA compliance

GET  /api/dashboard/queue
  - Callback queue (sorted by priority + callbackDueAt)

GET  /api/dashboard/map
  - Victim locations for map display
```

---

## 2.5 Voice AI Integration

### Gemini 2.5 Flash Live Configuration

```python
# Conceptual configuration for voice AI

SYSTEM_PROMPT = """
You are an AI assistant for emergency calls. Your role is to:

1. Stay calm and reassuring
2. Collect critical information:
   - What is your situation? (flood, fire, earthquake, accident, medical, etc.)
   - How many people need help?
   - What is your location? (address, landmarks, GPS if known)
   - Is anyone injured? Describe injuries.
   - What immediate help do you need?
   - What phone number can we reach you at?

3. Assess severity:
   - RED: Life threatening, needs urgent medical support NOW
   - YELLOW: Injured/at risk but not immediately life threatening
   - GREEN: Safe, needs information or non-urgent help

4. Provide survival guidance based on their situation type

5. Confirm information back to caller

IMPORTANT:
- Never hang up until all information is collected
- If caller is panicked, speak slowly and calmly
- Always end with survival guidance relevant to their situation
- System is always available - not limited to specific crisis events
"""

# Function calling for structured output
# IMPORTANT: All argument values must be in English regardless of caller's language
FUNCTIONS = [
    {
        "name": "record_victim_info",
        "description": "Record collected victim information. ALL values MUST be in English.",
        "parameters": {
            "situation_type": "string",    # fire, flood, earthquake, medical, accident (English)
            "victim_count": "integer",
            "location": "string",          # Transliterate to English (e.g., Siam Paragon, Bangkok)
            "injuries": "string",          # none, minor cuts, broken leg, etc. (English)
            "help_needed": "string",       # rescue, medical, ambulance, shelter (English)
            "phone_number": "string",      # digits with country code
            "priority": "RED|YELLOW|GREEN",
            "priority_reason": "string",   # Brief explanation in English
            "primary_language": "string"   # Full name: Thai, English, Chinese, Burmese, etc.
        }
    },
    {
        "name": "get_survival_guide",
        "description": "Get survival instructions for situation type",
        "parameters": {
            "situation_type": "string"     # fire, flood, earthquake, medical
        }
    }
]
```

### Survival Guide Function (Hardcoded)

```python
# Hardcoded function that returns survival instructions
# Takes situation type and returns predefined guidance

def get_survival_guide(situation_type: str) -> str:
    """
    Returns predefined survival instructions based on situation type.
    AI improvises only when no preset exists.
    """
    guides = {
        "fire": """
            - Stay low to the ground - smoke rises
            - Find nearest exit, do not use elevators
            - Cover nose and mouth with wet cloth
            - If door is hot, do not open - find alternate exit
            - Stop, drop, and roll if clothes catch fire
        """,
        "flood": """
            - Do not walk or swim through floodwater
            - Move to higher ground immediately
            - Do not drive through flooded roads
            - Preserve clean drinking water
            - Avoid contact with electrical equipment
        """,
        "earthquake": """
            - Drop, cover, and hold on
            - Stay away from windows and exterior walls
            - If indoors, stay indoors until shaking stops
            - If outdoors, move to open area away from buildings
            - Expect aftershocks
        """,
        "medical": """
            - Stay calm and assess the situation
            - If bleeding, apply direct pressure with clean cloth
            - Do not move injured person unless in immediate danger
            - Keep injured person warm and comfortable
            - Stay on the line for further instructions
        """,
    }

    # Return preset if exists, otherwise return None (AI will improvise)
    return guides.get(situation_type.lower())
```

### Call Flow Implementation

```python
# Pseudocode for call handling with Firestore

async def handle_inbound_call(telephony_event):
    # 1. Initialize voice AI session
    ai_session = await gemini.create_live_session(
        system_prompt=SYSTEM_PROMPT,
        functions=FUNCTIONS
    )

    # 2. Connect Twilio audio to AI
    await connect_audio_stream(telephony_event, ai_session)

    # 3. Wait for AI to complete information gathering
    result = await ai_session.wait_for_completion()

    # 4. Get survival guidance
    guidance = get_survival_guide(result.situation_type)

    # 5. Generate ticket number and create victim document
    ticket_number = generate_ticket_number()  # C + YYYYMMDD + 6 random digits

    victim_ref = await db.collection('victims').document(ticket_number).set({
        'ticketNumber': ticket_number,
        'phoneNumber': telephony_event.from_number,
        'primaryLanguage': result.primary_language,  # Full name: Thai, English, etc.
        'location': {
            'text': result.location,
            'latitude': result.latitude,
            'longitude': result.longitude
        },
        'victimCount': result.victim_count,
        'condition': result.condition,
        'injuryDetails': result.injuries,
        'helpNeeded': result.help_needed,
        'situationType': result.situation_type,
        'priority': result.priority,
        'priorityReason': result.priority_reason,
        'status': 'pending',
        'createdAt': firestore.SERVER_TIMESTAMP,
        'updatedAt': firestore.SERVER_TIMESTAMP,
        'lastContactAt': firestore.SERVER_TIMESTAMP,
        'nextPulseAt': now() + timedelta(hours=1),
        'callbackDueAt': calculate_callback_deadline(result.priority),
        'aiTranscript': ai_session.transcript,
        'notes': '',
        'callHistory': [{
            'direction': 'inbound',
            'callType': 'initial',
            'startedAt': telephony_event.start_time,
            'durationSec': ai_session.duration,
            'summary': result.summary,
            'guidanceGiven': guidance,
            'telephonyId': telephony_event.call_sid
        }]
    })

def generate_ticket_number() -> str:
    """Generate ticket number: C + YYYYMMDD + 6 random digits"""
    now = datetime.now()
    date_part = now.strftime('%Y%m%d')
    random_part = str(random.randint(0, 999999)).zfill(6)
    return f"C{date_part}{random_part}"

def calculate_callback_deadline(priority: str) -> datetime:
    """Calculate callback deadline based on priority"""
    now = datetime.now()
    if priority == 'RED':
        return now + timedelta(minutes=10)
    elif priority == 'YELLOW':
        return now + timedelta(minutes=30)
    else:  # GREEN
        return now + timedelta(hours=24)  # No strict SLA, but track anyway
```

---

## 2.6 Scheduler Service

### Pulse Check Scheduler

```python
# Runs every minute (Cloud Function or cron job)

async def pulse_check_scheduler():
    # Find ALL victims due for pulse check (1 hour since last contact)
    now = datetime.now()

    victims_ref = db.collection('victims')
    query = victims_ref.where('status', '==', 'pending') \
                       .where('nextPulseAt', '<=', now) \
                       .limit(10)

    victims = query.stream()

    for victim in victims:
        victim_data = victim.to_dict()

        # Queue outbound pulse check call
        await queue_outbound_call(
            victim_id=victim.id,
            call_type="pulse_check"
        )

        # Update next pulse check time (1 hour from now)
        victim.reference.update({
            'nextPulseAt': now + timedelta(hours=1),
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
```

### SLA Monitor

```python
# Runs every minute - alerts on SLA breaches

async def sla_monitor():
    now = datetime.now()

    # Find victims past their callback deadline
    victims_ref = db.collection('victims')
    query = victims_ref.where('status', '==', 'pending') \
                       .where('callbackDueAt', '<', now)

    overdue = query.stream()

    for victim in overdue:
        victim_data = victim.to_dict()

        await send_alert(
            type="SLA_BREACH",
            victim_id=victim.id,
            priority=victim_data['priority'],
            overdue_by=now - victim_data['callbackDueAt']
        )
```

---

## 2.7 Security & Privacy (Demo)

### Access Control

**Demo**: No authentication - open access for demo purposes.

**Future (Production)**:
| Role | Victim Panel | Resource Panel | Admin |
|------|--------------|----------------|-------|
| Operator | Read/Write | Read | - |
| Coordinator | Read/Write | Read/Write | - |
| Admin | Full | Full | Full |

### Data Protection (Demo)

```python
# Demo: No access control, direct Firestore access
# Future: Add Firebase Auth + Firestore Security Rules

async def get_victim(victim_id: str):
    doc = db.collection('victims').document(victim_id).get()
    return doc.to_dict() if doc.exists else None
```

### Data Retention (Future)

```python
# Cleanup closed cases after 90 days (future implementation)

async def cleanup_old_cases():
    cutoff = datetime.now() - timedelta(days=90)

    victims_ref = db.collection('victims')
    query = victims_ref.where('status', '==', 'closed') \
                       .where('updatedAt', '<', cutoff)

    for victim in query.stream():
        # Anonymize victim data
        victim.reference.update({
            'phoneNumber': 'REDACTED',
            'location': {'text': 'REDACTED'},
            'aiTranscript': firestore.DELETE_FIELD
        })
```

### AI Training Exclusion

- All calls processed via API only (no training)
- Data processing agreements with AI providers
- Victim data never leaves controlled infrastructure for training

---

## 2.8 Deployment Architecture (Demo)

### Simplified Setup

```
                        ┌─────────────────┐
                        │     Twilio      │
                        │   (Webhooks)    │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   API Server    │
                        │ (Vercel/Cloud   │
                        │   Functions)    │
                        └────────┬────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
       │  Firestore  │   │   Gemini    │   │  Dashboard  │
       │  (Database) │   │  (Voice AI) │   │  (Next.js)  │
       └─────────────┘   └─────────────┘   └─────────────┘
```

### Demo Architecture Benefits

- **Serverless**: No servers to manage
- **Auto-scaling**: Firebase/Vercel handle scaling automatically
- **Real-time**: Firestore listeners for live dashboard updates
- **Low cost**: Pay-per-use pricing for demo scale

### Failover Strategy (Future)

1. **Application**: Serverless auto-scales
2. **Database**: Firestore has built-in redundancy
3. **Telephony**: Twilio has global redundancy
4. **AI**: Fallback to alternative model if primary unavailable
5. **Ultimate fallback**: Route to human operators (traditional mode)

---

## 2.9 Monitoring & Alerting

### Key Metrics

| Metric | Alert Threshold |
|--------|-----------------|
| Call answer rate | < 99% |
| AI response latency | > 2 seconds |
| RED callback SLA | Any breach |
| YELLOW callback SLA | > 5% breach |
| System error rate | > 1% |
| Database connections | > 80% pool |

### Dashboard Metrics

```
Real-time Display:
├── Active calls (current)
├── Queue depth by priority
├── SLA compliance (last hour)
├── Callback completion rate
└── Resource availability
```

---

## 2.10 Cost Estimation (Demo)

### Per-Call Costs

| Component | Cost |
|-----------|------|
| Gemini 2.5 Flash Live | ~$0.02-0.03/min |
| Twilio Voice | ~$0.01/min |
| Infrastructure | ~$0.001/min (serverless) |
| **Total** | **~$0.031-0.041/min** |

### Monthly Infrastructure (Demo)

| Component | Estimated Cost |
|-----------|---------------|
| Firebase Firestore | $0-25 (free tier covers demo) |
| Vercel/Firebase Functions | $0-20 (free tier covers demo) |
| Twilio Phone Number | $1-2/month |
| **Total** | **$1-50/month (demo scale)** |

### Production Scale (Future)

| Component | Estimated Cost |
|-----------|---------------|
| Firebase Firestore | $50-200/month |
| Cloud Functions | $50-150/month |
| Twilio (numbers + usage) | $100-500/month |
| Monitoring | $20-50/month |
| **Total** | **$220-900/month** |

---

## 2.11 Development Phases

### Phase 1: Demo MVP (COMPLETED)
- [x] Twilio webhook integration
- [x] Gemini 2.5 Flash Live voice AI
- [x] Simple triage (RED/YELLOW/GREEN)
- [x] Firestore: victims collection (with ticket number as ID)
- [x] Firestore: resources collection
- [x] Hardcoded survival guide function (Thai language)
- [x] Cases dashboard (view/filter/status actions)
- [x] Resources dashboard (view/allocate)
- [x] Pulse Check dashboard
- [x] Multi-language detection (full language names)
- [x] Tool arguments in English only
- [x] Firebase Hosting deployment
- [x] Cloud Run deployment for bot

### Phase 2: Core Features
- [ ] Outbound pulse checks (automated scheduler)
- [ ] SLA monitoring with alerts
- [ ] Call history recording
- [ ] Resource allocation from case detail

### Phase 3: Production Ready
- [ ] Firebase Auth integration
- [ ] Firestore security rules
- [ ] Emergency services portal (read-only)
- [ ] Advanced analytics
- [ ] Mobile-responsive dashboard

### Phase 4: Future
- [ ] Damage assessment integration
- [ ] Catastrophe alert integration
- [ ] Commercial mode switching
- [ ] Post-crisis reporting
- [ ] Insurance workflow integration

---

# APPENDIX

## A. Glossary

| Term | Definition |
|------|------------|
| **Triage** | Process of prioritizing victims based on severity |
| **Pulse Check** | Automated outbound call to check victim status |
| **SLA** | Service Level Agreement - callback time commitment |
| **RED/YELLOW/GREEN** | Priority levels for victim cases |

## B. References

- Gemini API Documentation
- Twilio Voice API
- FEMA Emergency Response Guidelines

## C. Open Items

- [ ] Pilot partner selection
- [ ] Fire/flood damage assessment data sources
- [ ] Country-specific catastrophe alert integrations
- [ ] Detailed compliance requirements (PDPA, GDPR)

---

*Document Version: 1.0*
*Last Updated: December 2025*
