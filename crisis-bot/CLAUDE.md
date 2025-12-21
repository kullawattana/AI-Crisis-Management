# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Crisis Communication System - an AI-powered call center that handles emergency calls. AI collects victim information, triages by severity, provides survival guidance, and enables prioritized human callbacks.

**Current Status**: Demo implementation phase. See `CRISIS_BOT_SPEC.md` for full system design.

## Demo Architecture

```
Twilio (Webhooks) → Voice AI (Gemini 2.5 Flash Live) → API Server → Firestore
                                                            ↓
                                                   Dashboard (Next.js)
```

### Core Components (Demo)
- **Voice AI**: Gemini 2.5 Flash Live for real-time voice conversation
- **Telephony**: Twilio for phone number and webhooks
- **Backend**: Python or Node.js API server (serverless)
- **Database**: Firebase Firestore (2 collections: victims, resources)
- **Dashboard**: React/Next.js for operator interface
- **Auth**: Skipped for demo

### Firestore Collections
- **victims**: Victim info + embedded callHistory array
- **resources**: Resource info + embedded allocations array

### Triage System
- **RED**: Life threatening → Human callback ≤ 10 minutes
- **YELLOW**: Injured/at risk → Human callback ≤ 30 minutes
- **GREEN**: Safe → Human callback when available
- **All cases**: AI pulse check every 1 hour since last contact

### Demo Simplifications
- No crisis isolation - system always available for any situation type
- No user authentication
- Survival guides hardcoded in function (not database)
- Call logs embedded in victim documents
- Resource allocations embedded in resource documents

## Tech Stack (Demo)

| Layer | Technology |
|-------|------------|
| Voice AI | Gemini 2.5 Flash Live |
| Telephony | Twilio |
| Backend | Python / Node.js (serverless) |
| Database | Firebase Firestore |
| Dashboard | React / Next.js |
| Hosting | Firebase / Vercel |

## Key Design Principles

1. **AI extends humans, doesn't replace** - AI handles intake and triage, humans make decisions and authorize actions
2. **Multi-language support** - Auto-detect and respond in victim's language; store primaryLanguage for human callback
3. **Predetermined survival guidance** - Hardcoded function returns vetted scripts per situation type, AI improvises only when no preset exists
4. **Human callback in ALL cases** - AI is data collector + prioritizer, not decision maker
5. **Always available** - No crisis mode switching, system handles any emergency situation anytime
