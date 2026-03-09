"""Bot configuration - loads from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

# Azure Bot Service credentials
# For managed identity auth, APP_PASSWORD is empty and APP_TENANT_ID is set.
BOT_APP_ID = os.getenv("BOT_APP_ID", "")
BOT_APP_PASSWORD = os.getenv("BOT_APP_PASSWORD", "")
BOT_APP_TENANT_ID = os.getenv("BOT_APP_TENANT_ID", "")
BOT_APP_TYPE = os.getenv("BOT_APP_TYPE", "SingleTenant")

# Server
PORT = int(os.getenv("PORT", "3978"))
