# Teams App Setup Instructions

## Prerequisites

1. Azure subscription access
2. Teams admin access
3. App Studio or Developer Portal for Teams

## Step 1: Create Teams App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Enter name: "Lunch Order Bot"
5. Select "Accounts in this organizational directory only"
6. Click "Register"
7. Copy the "Application (client) ID" - this is your `TEAMS_APP_ID`

## Step 2: Configure Authentication

1. In your app registration, go to "Certificates & secrets"
2. Click "New client secret"
3. Add description: "Lunch Order Bot Secret"
4. Select expiration (recommend: 24 months)
5. Click "Add"
6. Copy the secret value - this is your `TEAMS_BOT_PASSWORD`

## Step 3: Create Bot Resource

```bash
# Login to Azure
az login
az account set --subscription e9b64842-3c87-4665-ad56-86ae7c20fe4b

# Create bot
az bot create \
  --resource-group rg-lunch-ordering-prod \
  --name bot-lunch-ordering \
  --kind registration \
  --app-type MultiTenant \
  --appid YOUR-APP-ID-HERE \
  --password YOUR-APP-PASSWORD-HERE \
  --endpoint https://YOUR-APP-URL.azurewebsites.net/api/messages

# Enable Teams channel
az bot msteams create \
  --resource-group rg-lunch-ordering-prod \
  --name bot-lunch-ordering
```

## Step 4: Configure Manifest

1. Edit `teams-app/manifest.json`
2. Replace placeholders:
   - `YOUR-APP-ID-HERE` with your Application ID
   - `YOUR-BOT-ID-HERE` with your Bot ID
   - `YOUR-APP-URL` with your deployed app URL

## Step 5: Package and Upload

```bash
# Create app package
cd teams-app
zip -r ../lunch-order-teams-app.zip *

# Upload to Teams:
# 1. Open Teams
# 2. Go to Apps > Manage your apps
# 3. Click "Upload an app"
# 4. Select "Upload a custom app"
# 5. Choose the lunch-order-teams-app.zip file
```

## Step 6: Test the Bot

1. In Teams, search for "Lunch Order"
2. Click on the app
3. Click "Add"
4. Try commands:
   - `/help`
   - `/order`
   - `/mydefault`

## Environment Variables

Add these to your `.env` file:

```
TEAMS_BOT_ID=your-bot-id
TEAMS_BOT_PASSWORD=your-bot-password
TEAMS_TENANT_ID=your-tenant-id
TEAMS_APP_ID=your-app-id
```

## Troubleshooting

### Bot doesn't respond
- Check bot endpoint is accessible
- Verify bot ID and password are correct
- Check Application Insights for errors

### Can't upload app
- Ensure manifest.json is valid
- Check all URLs are accessible
- Verify app ID matches registration

### Authentication fails
- Verify client secret hasn't expired
- Check tenant ID is correct
- Ensure app has correct permissions

## Next Steps

1. Implement bot message handlers
2. Create adaptive cards for orders
3. Set up proactive messaging
4. Add rich interactions

For detailed implementation, see PROJECT_SPEC.md Phase 8.
