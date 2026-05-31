# Deploy Backend To Azure Container Apps

This document explains how to deploy the `crisis-bot` backend to Azure so Twilio can call the webhook through a public HTTPS URL.

## Prerequisites

1. Azure CLI is installed.
2. You are logged in to Azure.
3. You have permission to create a Resource Group, ACR, and Container Apps.
4. Keys have been configured in `crisis-bot/.env`.

Check login:

```bash
az login
az account show
```

## Deploy

Run from the repo root:

```bash
cd crisis-bot
bash scripts/deploy_azure_container_app.sh
```

The script creates or updates:

- Azure Resource Group
- Azure Container Registry
- Azure Container Apps Environment
- Azure Container App for the backend

It also builds the Docker image from `crisis-bot/Dockerfile` using Azure Container Registry remote build.

## Default Values

If no overrides are configured, the script uses:

```env
AZURE_RESOURCE_GROUP=rg-crisis-bot-dev
AZURE_LOCATION=southeastasia
CONTAINER_APP_ENV=crisis-bot-env
CONTAINER_APP_NAME=crisis-bot
```

To change the names, add values in `crisis-bot/.env`:

```env
AZURE_RESOURCE_GROUP=rg-crisis-bot-prod
AZURE_LOCATION=southeastasia
AZURE_ACR_NAME=youruniqueacrname
CONTAINER_APP_ENV=crisis-bot-env
CONTAINER_APP_NAME=crisis-bot
```

## After Deploy

At the end of the command, you will get a URL similar to:

```text
https://crisis-bot.<region>.azurecontainerapps.io
```

**Current Azure test URL for this project:**

```text
https://crisis-bot.livelyforest-b853572a.southeastasia.azurecontainerapps.io
```

**Current Twilio webhook for this project:**

```text
https://crisis-bot.livelyforest-b853572a.southeastasia.azurecontainerapps.io/incoming-call
```

Put this URL in Twilio:

```text
Phone Numbers > Manage > Active numbers > your number > Voice Configuration
```

Configure:

```text
A call comes in: Webhook
URL: https://your-container-app-url/incoming-call
Method: POST
```

## Dashboard

The dashboard can run locally or be deployed as an Azure Storage Static Website.

### Local Dashboard

If the dashboard runs locally, set:

```env
VITE_API_BASE_URL=https://crisis-bot.livelyforest-b853572a.southeastasia.azurecontainerapps.io
```

In:

```bash
crisis-bot/dashboard/.env.local
```

Then run:

```bash
cd crisis-bot/dashboard
npm run dev
```

### Azure Cloud Dashboard

If you want a dashboard URL on Azure without using `localhost`, run:

```bash
cd crisis-bot
./scripts/deploy_dashboard_azure_storage.sh
```

The script will:

- Build the React dashboard.
- Create or use an Azure Storage Account.
- Enable Static Website hosting.
- Upload `dashboard/dist` to `$web`.
- Update backend Container App CORS so the dashboard URL can call the API.

After a successful deployment, the command prints a URL such as:

```text
https://crisisdashxxxxxxxx.z23.web.core.windows.net/
```
