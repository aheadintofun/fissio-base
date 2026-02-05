# Azure Deployment Guide

Complete instructions for deploying fissio-base and the full Fissio platform to Azure using Container Apps.

## Architecture Overview

```
                          Azure Front Door (CDN + WAF)
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
         ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
         │ fissio-site  │ │ fissio-docs  │ │ fissio-crmi  │
         │ Container App│ │ Container App│ │ Container App│
         └──────────────┘ └──────────────┘ └──────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
         ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
         │ fissio-base  │ │   Azure      │ │   Azure      │
         │ Container App│ │  PostgreSQL  │ │    Blob      │
         └──────────────┘ └──────────────┘ └──────────────┘
```

## Prerequisites

### Local Tools

```bash
# Install Azure CLI
brew install azure-cli

# Install Docker
brew install --cask docker

# Login to Azure
az login

# Set subscription (if you have multiple)
az account set --subscription "Your Subscription Name"
```

### Azure Resources Needed

| Resource | Purpose | Estimated Cost |
|----------|---------|----------------|
| Resource Group | Container for all resources | Free |
| Container Registry | Store Docker images | ~$5/month (Basic) |
| Container Apps Environment | Run containers | Pay-per-use |
| Container Apps (x4) | Run each Fissio app | ~$0.000024/vCPU-s |
| Azure PostgreSQL Flexible | Database for CRM | ~$15/month (Burstable) |
| Azure Blob Storage | File storage | ~$0.02/GB/month |
| Azure Front Door | CDN + SSL + WAF | ~$35/month |

**Estimated total: ~$60-100/month** for a small deployment

---

## Step 1: Create Azure Resources

### 1.1 Set Variables

```bash
# Configuration - EDIT THESE
RESOURCE_GROUP="fissio-prod"
LOCATION="eastus"
ACR_NAME="fissioacr"  # Must be globally unique, lowercase
ENVIRONMENT="fissio-env"

# App names
SITE_APP="fissio-site"
DOCS_APP="fissio-docs"
CRMI_APP="fissio-crmi"
BASE_APP="fissio-base"
```

### 1.2 Create Resource Group

```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### 1.3 Create Container Registry

```bash
# Create registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Get login credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Login to registry
az acr login --name $ACR_NAME

echo "Registry: $ACR_NAME.azurecr.io"
echo "Username: $ACR_USERNAME"
```

### 1.4 Create Container Apps Environment

```bash
# Install Container Apps extension
az extension add --name containerapp --upgrade

# Create the environment
az containerapp env create \
  --name $ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### 1.5 Create PostgreSQL (for fissio-crmi)

```bash
# Create PostgreSQL Flexible Server
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name fissio-postgres \
  --location $LOCATION \
  --admin-user fissio_admin \
  --admin-password "YourSecurePassword123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 15

# Create database
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name fissio-postgres \
  --database-name fissio_crm

# Allow Azure services to connect
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name fissio-postgres \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### 1.6 Create Blob Storage

```bash
# Create storage account
az storage account create \
  --name fissiostorage \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Create containers
az storage container create \
  --name documents \
  --account-name fissiostorage

az storage container create \
  --name uploads \
  --account-name fissiostorage

# Get connection string
STORAGE_CONNECTION=$(az storage account show-connection-string \
  --name fissiostorage \
  --resource-group $RESOURCE_GROUP \
  --query connectionString -o tsv)
```

---

## Step 2: Build and Push Docker Images

### 2.1 Build and Push fissio-base

fissio-base has multiple services. For Azure deployment, we primarily deploy the frontend, with optional Jupyter and Superset containers.

```bash
# From the fissio-base directory
# Build frontend
docker build -t $ACR_NAME.azurecr.io/fissio-base-frontend:latest ./app
docker push $ACR_NAME.azurecr.io/fissio-base-frontend:latest
```

### 2.2 Build Other Apps

```bash
# fissio-site
cd ~/fissio-site
docker build -t $ACR_NAME.azurecr.io/fissio-site:latest .
docker push $ACR_NAME.azurecr.io/fissio-site:latest

# fissio-docs
cd ~/fissio-docs
docker build -t $ACR_NAME.azurecr.io/fissio-docs:latest .
docker push $ACR_NAME.azurecr.io/fissio-docs:latest

# fissio-crmi
cd ~/fissio-crmi
docker build -t $ACR_NAME.azurecr.io/fissio-crmi:latest .
docker push $ACR_NAME.azurecr.io/fissio-crmi:latest
```

---

## Step 3: Deploy Container Apps

### 3.1 Deploy fissio-base (Frontend + Optional Services)

```bash
# Deploy frontend
az containerapp create \
  --name $BASE_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --image $ACR_NAME.azurecr.io/fissio-base-frontend:latest \
  --registry-server $ACR_NAME.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8080 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 2 \
  --cpu 0.25 \
  --memory 0.5Gi \
  --env-vars \
    "JUPYTER_URL=https://fissio-jupyter.azurecontainerapps.io" \
    "SUPERSET_URL=https://fissio-superset.azurecontainerapps.io" \
    "DUCKDB_URL=https://fissio-duckdb.azurecontainerapps.io"

# Deploy Jupyter (optional - can use Azure ML Notebooks instead)
az containerapp create \
  --name fissio-jupyter \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --image quay.io/jupyter/scipy-notebook:latest \
  --target-port 8888 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 1 \
  --cpu 1.0 \
  --memory 2Gi \
  --env-vars \
    "JUPYTER_TOKEN=secretref:jupyter-token"

az containerapp secret set \
  --name fissio-jupyter \
  --resource-group $RESOURCE_GROUP \
  --secrets "jupyter-token=your_secure_jupyter_token"

# Deploy Superset
az containerapp create \
  --name fissio-superset \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --image apache/superset:latest \
  --target-port 8088 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 2 \
  --cpu 1.0 \
  --memory 2Gi \
  --env-vars \
    "SUPERSET_SECRET_KEY=secretref:superset-secret"

az containerapp secret set \
  --name fissio-superset \
  --resource-group $RESOURCE_GROUP \
  --secrets "superset-secret=$(openssl rand -base64 32)"
```

### 3.2 Deploy fissio-site

```bash
az containerapp create \
  --name $SITE_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --image $ACR_NAME.azurecr.io/fissio-site:latest \
  --registry-server $ACR_NAME.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1Gi \
  --env-vars \
    "MAPBOX_TOKEN=secretref:mapbox-token" \
    "DOCS_API_URL=https://fissio-docs.azurecontainerapps.io"

az containerapp secret set \
  --name $SITE_APP \
  --resource-group $RESOURCE_GROUP \
  --secrets "mapbox-token=your_mapbox_token_here"
```

### 3.3 Deploy fissio-docs

```bash
az containerapp create \
  --name $DOCS_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --image $ACR_NAME.azurecr.io/fissio-docs:latest \
  --registry-server $ACR_NAME.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8001 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 1.0 \
  --memory 2Gi \
  --env-vars \
    "OPENAI_API_KEY=secretref:openai-key" \
    "AZURE_STORAGE_CONNECTION_STRING=secretref:storage-conn"

az containerapp secret set \
  --name $DOCS_APP \
  --resource-group $RESOURCE_GROUP \
  --secrets \
    "openai-key=your_openai_api_key" \
    "storage-conn=$STORAGE_CONNECTION"
```

### 3.4 Deploy fissio-crmi

```bash
PG_HOST="fissio-postgres.postgres.database.azure.com"
PG_USER="fissio_admin"
PG_PASS="YourSecurePassword123!"
PG_DB="fissio_crm"

az containerapp create \
  --name $CRMI_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --image $ACR_NAME.azurecr.io/fissio-crmi:latest \
  --registry-server $ACR_NAME.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 3000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1Gi \
  --env-vars \
    "DATABASE_URL=secretref:database-url" \
    "NODE_ENV=production"

az containerapp secret set \
  --name $CRMI_APP \
  --resource-group $RESOURCE_GROUP \
  --secrets "database-url=postgresql://$PG_USER:$PG_PASS@$PG_HOST:5432/$PG_DB?sslmode=require"
```

---

## Step 4: Configure Custom Domains

### 4.1 Get Default URLs

```bash
az containerapp show --name $BASE_APP --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv
```

### 4.2 Add Custom Domain

```bash
az containerapp hostname add \
  --name $BASE_APP \
  --resource-group $RESOURCE_GROUP \
  --hostname "analytics.fissio.com"

az containerapp hostname bind \
  --name $BASE_APP \
  --resource-group $RESOURCE_GROUP \
  --hostname "analytics.fissio.com" \
  --environment $ENVIRONMENT \
  --validation-method CNAME
```

**DNS Configuration**:

| Type | Name | Value |
|------|------|-------|
| CNAME | @ | fissio-site.azurecontainerapps.io |
| CNAME | docs | fissio-docs.azurecontainerapps.io |
| CNAME | crm | fissio-crmi.azurecontainerapps.io |
| CNAME | analytics | fissio-base.azurecontainerapps.io |

---

## Step 5: Set Up CI/CD with GitHub Actions

### 5.1 Create Service Principal

```bash
az ad sp create-for-rbac \
  --name "fissio-github-actions" \
  --role contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth

# Save the JSON output as a GitHub secret named AZURE_CREDENTIALS
```

### 5.2 GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Build and Deploy to Azure

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  AZURE_CONTAINER_REGISTRY: fissioacr.azurecr.io
  CONTAINER_APP_NAME: fissio-base
  RESOURCE_GROUP: fissio-prod

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Login to Container Registry
        uses: azure/docker-login@v1
        with:
          login-server: ${{ env.AZURE_CONTAINER_REGISTRY }}
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}

      - name: Build and push image
        run: |
          docker build -t ${{ env.AZURE_CONTAINER_REGISTRY }}/${{ env.CONTAINER_APP_NAME }}-frontend:${{ github.sha }} ./app
          docker build -t ${{ env.AZURE_CONTAINER_REGISTRY }}/${{ env.CONTAINER_APP_NAME }}-frontend:latest ./app
          docker push ${{ env.AZURE_CONTAINER_REGISTRY }}/${{ env.CONTAINER_APP_NAME }}-frontend:${{ github.sha }}
          docker push ${{ env.AZURE_CONTAINER_REGISTRY }}/${{ env.CONTAINER_APP_NAME }}-frontend:latest

      - name: Deploy to Container App
        uses: azure/container-apps-deploy-action@v1
        with:
          resourceGroup: ${{ env.RESOURCE_GROUP }}
          containerAppName: ${{ env.CONTAINER_APP_NAME }}
          imageToDeploy: ${{ env.AZURE_CONTAINER_REGISTRY }}/${{ env.CONTAINER_APP_NAME }}-frontend:${{ github.sha }}
```

### 5.3 Add GitHub Secrets

| Secret Name | Value |
|-------------|-------|
| `AZURE_CREDENTIALS` | JSON from service principal creation |
| `ACR_USERNAME` | Container registry username |
| `ACR_PASSWORD` | Container registry password |

---

## Step 6: Monitoring and Logging

```bash
# Create Application Insights
az monitor app-insights component create \
  --app fissio-insights \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --application-type web

# Stream logs
az containerapp logs show \
  --name $BASE_APP \
  --resource-group $RESOURCE_GROUP \
  --follow
```

---

## Step 7: Scaling Configuration

```bash
# Scale Jupyter to zero when not in use (cost savings)
az containerapp update \
  --name fissio-jupyter \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 0 \
  --max-replicas 1

# Scale frontend based on HTTP requests
az containerapp update \
  --name $BASE_APP \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 1 \
  --max-replicas 5 \
  --scale-rule-name http-scaling \
  --scale-rule-type http \
  --scale-rule-http-concurrency 100
```

---

## Quick Reference

### URLs After Deployment

| App | Default URL | Custom Domain |
|-----|-------------|---------------|
| fissio-site | fissio-site.azurecontainerapps.io | fissio.com |
| fissio-docs | fissio-docs.azurecontainerapps.io | docs.fissio.com |
| fissio-crmi | fissio-crmi.azurecontainerapps.io | crm.fissio.com |
| fissio-base | fissio-base.azurecontainerapps.io | analytics.fissio.com |
| Jupyter | fissio-jupyter.azurecontainerapps.io | - |
| Superset | fissio-superset.azurecontainerapps.io | - |

### Useful Commands

```bash
# List all container apps
az containerapp list --resource-group $RESOURCE_GROUP -o table

# Restart an app
az containerapp revision restart \
  --name $BASE_APP \
  --resource-group $RESOURCE_GROUP

# Update environment variable
az containerapp update \
  --name $BASE_APP \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars "NEW_VAR=value"

# Delete everything (careful!)
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

### Cost Optimization Tips

1. **Scale Jupyter to zero** when not in use
2. Use **Burstable PostgreSQL** tier for small workloads
3. Use **Basic Container Registry** tier initially
4. Enable **auto-scaling** to handle traffic spikes efficiently
5. Use **Azure Reservations** for 1-3 year commitments (up to 65% savings)
6. Consider **Azure ML Notebooks** as alternative to self-hosted Jupyter

---

## Troubleshooting

### Container won't start

```bash
az containerapp logs show --name $BASE_APP --resource-group $RESOURCE_GROUP
az containerapp revision list --name $BASE_APP --resource-group $RESOURCE_GROUP -o table
```

### Image pull errors

```bash
az acr repository show-tags --name $ACR_NAME --repository fissio-base-frontend

az containerapp registry set \
  --name $BASE_APP \
  --resource-group $RESOURCE_GROUP \
  --server $ACR_NAME.azurecr.io \
  --username $ACR_USERNAME \
  --password $ACR_PASSWORD
```

### Superset initialization

Superset requires initial setup. After deploying, exec into the container:

```bash
# Initialize Superset database
superset db upgrade
superset fab create-admin --username admin --firstname Admin --lastname User --email admin@fissio.com --password admin
superset init
```
