#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DASHBOARD_DIR="${APP_DIR}/dashboard"

if ! command -v az >/dev/null 2>&1; then
  echo "Azure CLI is required. Install it first: https://learn.microsoft.com/cli/azure/install-azure-cli"
  exit 1
fi

if ! az account show >/dev/null 2>&1; then
  echo "Azure CLI is not logged in. Run: az login"
  exit 1
fi

AZURE_RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-rg-crisis-bot-dev}"
AZURE_LOCATION="${AZURE_LOCATION:-southeastasia}"
CONTAINER_APP_NAME="${CONTAINER_APP_NAME:-crisis-bot}"
SUBSCRIPTION_ID="$(az account show --query id -o tsv)"
SUFFIX="$(printf "%s" "${SUBSCRIPTION_ID}" | shasum | awk '{print substr($1,1,8)}')"
DASHBOARD_STORAGE_ACCOUNT="${DASHBOARD_STORAGE_ACCOUNT:-crisisdash${SUFFIX}}"
BACKEND_URL="${VITE_API_BASE_URL:-https://crisis-bot.livelyforest-b853572a.southeastasia.azurecontainerapps.io}"

echo "Building dashboard with API base: ${BACKEND_URL}"
(
  cd "${DASHBOARD_DIR}"
  VITE_API_BASE_URL="${BACKEND_URL}" npm run build
)

echo "Ensuring resource group: ${AZURE_RESOURCE_GROUP}"
az group create \
  --name "${AZURE_RESOURCE_GROUP}" \
  --location "${AZURE_LOCATION}" \
  --output none

echo "Ensuring storage account: ${DASHBOARD_STORAGE_ACCOUNT}"
if ! az storage account show --name "${DASHBOARD_STORAGE_ACCOUNT}" --resource-group "${AZURE_RESOURCE_GROUP}" >/dev/null 2>&1; then
  az storage account create \
    --name "${DASHBOARD_STORAGE_ACCOUNT}" \
    --resource-group "${AZURE_RESOURCE_GROUP}" \
    --location "${AZURE_LOCATION}" \
    --sku Standard_LRS \
    --kind StorageV2 \
    --output none
fi

STORAGE_ACCOUNT_KEY="$(az storage account keys list \
  --resource-group "${AZURE_RESOURCE_GROUP}" \
  --account-name "${DASHBOARD_STORAGE_ACCOUNT}" \
  --query '[0].value' \
  -o tsv)"

az storage blob service-properties update \
  --account-name "${DASHBOARD_STORAGE_ACCOUNT}" \
  --account-key "${STORAGE_ACCOUNT_KEY}" \
  --static-website \
  --index-document index.html \
  --404-document index.html \
  --output none

echo "Uploading dashboard files..."
az storage blob upload-batch \
  --account-name "${DASHBOARD_STORAGE_ACCOUNT}" \
  --account-key "${STORAGE_ACCOUNT_KEY}" \
  --destination '$web' \
  --source "${DASHBOARD_DIR}/dist" \
  --overwrite true \
  --output none

DASHBOARD_URL="$(az storage account show \
  --name "${DASHBOARD_STORAGE_ACCOUNT}" \
  --resource-group "${AZURE_RESOURCE_GROUP}" \
  --query "primaryEndpoints.web" \
  -o tsv)"

echo "Updating backend CORS for dashboard URL..."
CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173,${DASHBOARD_URL%/}"
az containerapp update \
  --name "${CONTAINER_APP_NAME}" \
  --resource-group "${AZURE_RESOURCE_GROUP}" \
  --set-env-vars "CORS_ORIGINS=${CORS_ORIGINS}" \
  --output none

echo ""
echo "Dashboard deployed:"
echo "${DASHBOARD_URL}"
echo ""
echo "Backend API:"
echo "${BACKEND_URL}"
