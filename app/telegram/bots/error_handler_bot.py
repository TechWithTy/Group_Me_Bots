import logging
import traceback
import html
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Import settings
try:
    from app.telegram.core.config import settings
except ImportError:
    settings = type('Settings', (), {
        'TELEGRAM_BOT_TOKEN': 'YOUR_BOT_TOKEN'
    })()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

DEVELOPER_CHAT_ID = 123456789  # Replace with your chat ID

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and send to developer."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )
    
    await context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode="HTML")

async def bad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Trigger an error."""
    await context.bot.wrong_method_name()  # type: ignore

if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("bad_command", bad_command))
    application.add_error_handler(error_handler)
    
    application.run_polling()
