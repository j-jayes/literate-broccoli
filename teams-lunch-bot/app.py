"""Entry point: aiohttp web server hosting the Teams bot."""

import logging
import sys
import traceback

from aiohttp import web
from aiohttp.web import Request, Response

from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    InvokeResponse,
    TurnContext,
)
from botbuilder.schema import Activity

import config
from bot import LunchBot

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Bot Framework adapter
# Supports both managed identity (no password) and app password auth.
adapter_settings = BotFrameworkAdapterSettings(
    app_id=config.BOT_APP_ID,
    app_password=config.BOT_APP_PASSWORD,
    channel_auth_tenant=config.BOT_APP_TENANT_ID or None,
)
adapter = BotFrameworkAdapter(adapter_settings)


async def on_error(context: TurnContext, error: Exception) -> None:
    """Global error handler for the adapter."""
    logger.error("Unhandled error: %s", error)
    traceback.print_exc()
    await context.send_activity("Sorry, something went wrong. Please try again.")


adapter.on_turn_error = on_error

# Bot instance
bot = LunchBot()


async def messages(req: Request) -> Response:
    """Handle all incoming Bot Framework messages at /api/messages."""
    if req.content_type != "application/json":
        return Response(status=415)

    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    async def call_bot(turn_context: TurnContext):
        # Route to the appropriate handler based on activity type
        if turn_context.activity.type == "message":
            await bot.on_message(turn_context)
        elif turn_context.activity.type == "invoke":
            # Handle Adaptive Card Action.Execute
            invoke_value = turn_context.activity.value or {}
            response = await bot.on_adaptive_card_invoke(turn_context, invoke_value)

            # Return invoke response so Teams gets the updated card
            invoke_response = InvokeResponse(status=response.get("statusCode", 200), body=response)
            await turn_context.send_activity(
                Activity(
                    type="invokeResponse",
                    value=invoke_response,
                )
            )

    try:
        await adapter.process_activity(activity, auth_header, call_bot)
        return Response(status=201)
    except PermissionError:
        return Response(status=401, text="Unauthorized")
    except Exception as e:
        # Bot Framework raises generic exceptions for auth failures
        error_msg = str(e)
        if "Authorization" in error_msg or "token" in error_msg.lower() or "unauthorized" in error_msg.lower():
            logger.warning("Auth rejected: %s", error_msg)
            return Response(status=401, text="Unauthorized")
        logger.exception("Error processing activity")
        return Response(status=500, text=error_msg)


def init_app() -> web.Application:
    """Create and configure the aiohttp application."""
    app = web.Application()
    app.router.add_post("/api/messages", messages)
    return app


if __name__ == "__main__":
    app = init_app()
    logger.info("Starting bot on port %s", config.PORT)
    web.run_app(app, host="0.0.0.0", port=config.PORT)
