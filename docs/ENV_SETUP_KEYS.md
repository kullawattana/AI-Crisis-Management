# Environment Key Setup Guide

This guide explains where each key in `crisis-bot/.env` comes from, what it is used for, and which resources must be created first.

## Files To Edit

Backend:

```bash
crisis-bot/.env
```

Dashboard:

```bash
crisis-bot/dashboard/.env.local
```

## 1. OpenAI GPT Realtime

Used by the voice bot to speak with callers through GPT Realtime speech-to-speech.

```env
OPENAI_API_KEY=
OPENAI_REALTIME_MODEL=gpt-realtime
OPENAI_REALTIME_VOICE=alloy
```

Required setup:

1. Go to the OpenAI Platform.
2. Create an API key.
3. Put the key in `OPENAI_API_KEY`.
4. You can keep the default values for `OPENAI_REALTIME_MODEL` and `OPENAI_REALTIME_VOICE`.

Required: Yes, for the voice bot.

## 2. Twilio

Used to receive phone calls and stream audio into the backend.

```env
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

Required setup:

1. Go to the Twilio Console.
2. Buy or select a phone number.
3. Copy `Account SID` into `TWILIO_ACCOUNT_SID`.
4. Copy `Auth Token` into `TWILIO_AUTH_TOKEN`.
5. Put the Twilio phone number in `TWILIO_PHONE_NUMBER`.
6. Configure the Twilio number webhook to point to:

```text
https://your-public-backend-url/incoming-call
```

If you run locally, use a tunnel such as ngrok or Dev Tunnel, then put the public URL in Twilio.

Required: Yes, for real inbound calls.

## 3. Azure OpenAI

Used for triage, classifying cases as RED/YELLOW/GREEN with Azure OpenAI.

```env
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_API_VERSION=2024-10-21
```

Required setup:

1. Create an Azure OpenAI resource.
2. Deploy a model, such as a GPT chat/triage model.
3. Copy the endpoint, for example:

```text
https://your-resource.openai.azure.com/
```

4. Put the endpoint in `AZURE_OPENAI_ENDPOINT`.
5. Copy the API key from the Azure Portal into `AZURE_OPENAI_API_KEY`.
6. Put the deployment name in `AZURE_OPENAI_DEPLOYMENT`.
7. You can keep the default value for `AZURE_OPENAI_API_VERSION`.

Required: Yes, if you want real Azure triage.  
If this is not configured, the system falls back to rule-based triage.

## 4. Azure Cosmos DB

Used to store cases, dashboard data, and audit logs.

```env
AZURE_COSMOS_ENDPOINT=
AZURE_COSMOS_KEY=
AZURE_COSMOS_DATABASE=crisis_voiceops
AZURE_COSMOS_CASES_CONTAINER=cases
AZURE_COSMOS_RESOURCES_CONTAINER=resources
AZURE_COSMOS_AUDIT_CONTAINER=audit_logs
```

Required setup:

1. Create an Azure Cosmos DB for NoSQL account.
2. Copy the URI/endpoint into `AZURE_COSMOS_ENDPOINT`.
3. Copy the primary key into `AZURE_COSMOS_KEY`.
4. You can keep the default database and container values.

Note:

The current code automatically creates the database and containers when the key is valid:

- `crisis_voiceops`
- `cases`
- `resources`
- `audit_logs`

Required: Yes, if you want persistent data storage on Azure.  
If this is not configured, the system falls back to an in-memory store, and data is lost on restart.

## 5. Azure Service Bus

Used to publish events such as `case.created` and `triage.completed` for future workflow integrations.

```env
AZURE_SERVICE_BUS_CONNECTION_STRING=
AZURE_SERVICE_BUS_TOPIC=crisis-events
AZURE_SERVICE_BUS_QUEUE=
```

Required setup:

1. Create an Azure Service Bus namespace.
2. Create a topic named `crisis-events`, or change the name if needed.
3. Copy the connection string into `AZURE_SERVICE_BUS_CONNECTION_STRING`.
4. If you use a topic, leave `AZURE_SERVICE_BUS_QUEUE` empty.
5. If you want to use a queue, put the queue name in `AZURE_SERVICE_BUS_QUEUE`.

Required: Yes, if you want real event workflows.  
If this is not configured, the system falls back to logging.

## 6. Azure AI Speech

Reserved for future STT/TTS or Azure Communication Services integration.

```env
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=southeastasia
AZURE_SPEECH_RECOGNITION_LANGUAGE=th-TH
AZURE_SPEECH_VOICE=th-TH-PremwadeeNeural
```

Required setup:

1. Create an Azure AI Speech resource.
2. Copy the key into `AZURE_SPEECH_KEY`.
3. Set the region to match the resource, for example `southeastasia`.
4. You can keep the default language and voice values if using Thai.

Required: Not required for the current flow because the voice bot uses OpenAI Realtime.

## 7. Optional Azure Platform Keys

```env
AZURE_MAPS_KEY=
APPLICATIONINSIGHTS_CONNECTION_STRING=
KEY_VAULT_URL=
```

Used for:

- `AZURE_MAPS_KEY`: Future maps/geocoding support.
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: Azure monitoring/logging.
- `KEY_VAULT_URL`: Secret storage in Azure Key Vault.

Required: Not required to run the MVP.

## 8. Dashboard API URL

File:

```bash
crisis-bot/dashboard/.env.local
```

Value:

```env
VITE_API_BASE_URL=http://localhost:9999
```

Required setup:

1. If the backend runs locally on port `9999`, keep the default value.
2. If the backend is deployed, change it to the real backend URL, for example:

```env
VITE_API_BASE_URL=https://your-backend-url
```

## Minimum Keys For Real Phone MVP

To make "call in and talk to the bot" work, configure at least:

```env
OPENAI_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

And configure the Twilio webhook:

```text
https://your-public-backend-url/incoming-call
```

## Azure-Connected Recommended Keys

For the recommended Azure-connected flow, also configure:

```env
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT=
AZURE_COSMOS_ENDPOINT=
AZURE_COSMOS_KEY=
AZURE_SERVICE_BUS_CONNECTION_STRING=
```

## Provider Mode

The current `.env` values are Azure-first:

```env
CASE_STORE_PROVIDER=cosmos
EVENT_PUBLISHER=service_bus
AI_TRIAGE_PROVIDER=azure_openai
VOICE_AI_PROVIDER=openai
```

If Azure keys are not ready, the code falls back automatically:

- Cosmos unavailable -> memory store
- Service Bus unavailable -> log
- Azure OpenAI unavailable -> rule-based triage
