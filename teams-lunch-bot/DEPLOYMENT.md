# Deploying LunchBot to Microsoft Teams

## Architecture

```
Teams Group Chat
    |
    | @LunchBot Pizzeria Napoli
    v
Azure Bot Service  -->  Your Python App (aiohttp on port 3978)
    |                        |
    |                        |-- Scraper: browses restaurant website
    |                        |-- LLM: extracts structured menu
    |                        |-- Returns Adaptive Card poll
    |
    v
Teams renders Adaptive Card in chat
    |
    | Users click checkboxes + Submit
    v
Action.Execute invoke -> Bot updates card with order summary
```

## Prerequisites

- Python 3.11+
- An Azure subscription (free tier works)
- Microsoft 365 tenant with Teams (your work account)
- Admin consent to sideload apps (or a Teams admin who can approve)

## Step 1: Register a Bot in Azure

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **"Azure Bot"** and click **Create**
3. Fill in:
   - **Bot handle:** `lunch-order-bot`
   - **Pricing tier:** F0 (Free)
   - **Microsoft App ID:** Create new -> **Multi Tenant**
4. Click **Create**
5. Once created, go to the resource:
   - Go to **Configuration** -> note the **Microsoft App ID**
   - Click **Manage Password** -> **New client secret** -> copy the **Value** (this is your `BOT_APP_PASSWORD`)
6. Go to **Channels** -> click **Microsoft Teams** -> Save

Save these values - you'll need them for `.env`.

## Step 2: Set Up a Tunnel (for local development)

The bot needs a public HTTPS URL. Use **dev tunnels** (built into VS Code) or **ngrok**.

### Option A: VS Code Dev Tunnel (recommended)
1. Open VS Code, press `Ctrl+Shift+P` -> "Ports: Forward a Port"
2. Forward port `3978`
3. Copy the tunnel URL (e.g., `https://abc123.devtunnels.ms`)

### Option B: ngrok
```bash
ngrok http 3978
```
Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

### Configure the messaging endpoint
Go back to your Azure Bot resource:
- **Configuration** -> **Messaging endpoint**: `https://<your-tunnel-url>/api/messages`
- Save

## Step 3: Configure and Run the Bot Locally

```bash
cd teams-lunch-bot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Create .env from template
cp .env.example .env
# Edit .env with your BOT_APP_ID, BOT_APP_PASSWORD, and LLM API keys

# Run
python app.py
```

The bot listens on `http://localhost:3978/api/messages`.

## Step 4: Create the Teams App Package

1. Edit `teams_app_manifest/manifest.json`:
   - Replace both `<<BOT_APP_ID>>` with your actual Microsoft App ID (GUID)
   - Update `validDomains` if needed (add your tunnel domain)

2. Replace the placeholder icons:
   - `color.png`: 192x192 color icon
   - `outline.png`: 32x32 transparent outline icon

3. Create the ZIP package:
```bash
cd teams_app_manifest
zip ../lunchbot.zip manifest.json color.png outline.png
```

## Step 5: Sideload to Teams

1. Open Microsoft Teams
2. Click **Apps** (left sidebar)
3. Click **Manage your apps** (bottom left)
4. Click **Upload an app** -> **Upload a custom app**
5. Select `lunchbot.zip`
6. Click **Add to a chat** and pick your group chat

If "Upload a custom app" is greyed out, your Teams admin needs to enable
**custom app sideloading** in the Teams Admin Center under
**Teams apps** -> **Setup policies** -> **Global** -> toggle **Upload custom apps**.

## Step 6: Use It

In the group chat:
```
@LunchBot Pizzeria Napoli
```
or:
```
@LunchBot https://restaurant-example.com/menu
```

The bot will:
1. Send a "working on it" message
2. Scrape the website using AI-guided navigation
3. Post an Adaptive Card with menu items as checkboxes
4. Each person selects items and clicks "Submit Order"
5. The card updates to show the combined order

## Production Deployment (Azure App Service)

For a persistent deployment (not relying on a local tunnel):

1. **Create an Azure App Service** (Python 3.11, B1 tier or higher)

2. **Deploy your code:**
```bash
# From the teams-lunch-bot directory
az webapp up --name lunch-order-bot --runtime "PYTHON:3.11" --sku B1
```

3. **Set environment variables** in the App Service:
```bash
az webapp config appsettings set --name lunch-order-bot --settings \
  BOT_APP_ID="your-app-id" \
  BOT_APP_PASSWORD="your-password" \
  AZURE_OPENAI_ENDPOINT="..." \
  AZURE_OPENAI_API_KEY="..."
```

4. **Configure startup command:**
```bash
az webapp config set --name lunch-order-bot --startup-file "python app.py"
```

5. **Update the Azure Bot messaging endpoint** to:
   `https://lunch-order-bot.azurewebsites.net/api/messages`

6. **Re-upload the Teams app package** (update `validDomains` in manifest.json
   to include `lunch-order-bot.azurewebsites.net`)

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Bot doesn't respond in Teams | Check messaging endpoint URL in Azure Bot config |
| "Something went wrong" | Check bot logs - likely a timeout on scraping. Try a direct URL |
| Can't upload custom app | Ask Teams admin to enable sideloading |
| Adaptive Card doesn't render | Ensure manifest version is 1.5+ and card schema version is 1.5 |
| Action.Execute not working | Ensure the bot is registered with Teams channel enabled |
| Orders not tracked across users | This is expected for local dev (in-memory). For production, add a database |
