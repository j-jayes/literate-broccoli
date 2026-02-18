#!/bin/bash

# Azure Deployment Script for Lunch Ordering System
# This script deploys the infrastructure and application to Azure

set -e

echo "==================================================="
echo "Azure Lunch Ordering System - Deployment Script"
echo "==================================================="

# Configuration
SUBSCRIPTION_ID="e9b64842-3c87-4665-ad56-86ae7c20fe4b"
RESOURCE_GROUP="rg-lunch-ordering-prod"
LOCATION="eastus"
ENVIRONMENT="prod"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed"
    echo "Please install from: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure
echo "Step 1: Logging into Azure..."
az login

# Set subscription
echo "Step 2: Setting subscription to $SUBSCRIPTION_ID..."
az account set --subscription "$SUBSCRIPTION_ID"

# Verify subscription
CURRENT_SUB=$(az account show --query id -o tsv)
if [ "$CURRENT_SUB" != "$SUBSCRIPTION_ID" ]; then
    echo "Error: Failed to set subscription"
    exit 1
fi
echo "✓ Subscription set successfully"

# Create resource group if it doesn't exist
echo "Step 3: Creating resource group..."
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --tags "Environment=$ENVIRONMENT" "Project=LunchOrdering"
echo "✓ Resource group created/verified"

# Deploy Bicep template
echo "Step 4: Deploying Azure infrastructure..."
DEPLOYMENT_NAME="lunch-ordering-deployment-$(date +%Y%m%d-%H%M%S)"

az deployment group create \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "$(dirname "$0")/../bicep/main.bicep" \
    --parameters environment="$ENVIRONMENT" \
    --verbose

echo "✓ Infrastructure deployed successfully"

# Get deployment outputs
echo "Step 5: Retrieving deployment outputs..."
SQL_SERVER=$(az deployment group show \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.outputs.sqlServerFqdn.value -o tsv)

REDIS_HOST=$(az deployment group show \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.outputs.redisCacheHostName.value -o tsv)

KEY_VAULT_URI=$(az deployment group show \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.outputs.keyVaultUri.value -o tsv)

APP_INSIGHTS_KEY=$(az deployment group show \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.outputs.appInsightsInstrumentationKey.value -o tsv)

echo "✓ Deployment outputs retrieved"

# Display deployment information
echo ""
echo "==================================================="
echo "Deployment Complete!"
echo "==================================================="
echo "Resource Group: $RESOURCE_GROUP"
echo "SQL Server: $SQL_SERVER"
echo "Redis Host: $REDIS_HOST"
echo "Key Vault: $KEY_VAULT_URI"
echo "Application Insights Key: $APP_INSIGHTS_KEY"
echo ""
echo "Next Steps:"
echo "1. Configure database connection strings"
echo "2. Deploy application code to App Services"
echo "3. Configure MS Teams bot"
echo "4. Test the application"
echo "==================================================="
