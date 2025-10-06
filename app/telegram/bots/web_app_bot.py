import logging
import json
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Import settings
try:
    from app.telegram.core.config import settings
except ImportError:
    settings = type('Settings', (), {
        'TELEGRAM_BOT_TOKEN': 'YOUR_BOT_TOKEN'
    })()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_web_app(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a WebApp button."""
    await update.message.reply_text(
        "Press the button to open the WebApp:",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Open WebApp",
                web_app=WebAppInfo(url="https://python-telegram-bot.org/static/webappbot")
            )
        ),
    )

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle WebApp data."""
    data = json.loads(update.effective_message.web_app_data.data)
    await update.message.reply_html(
        f"You selected color HEX: <code>{data['hex']}</code>",
        reply_markup=ReplyKeyboardRemove(),
    )

if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_web_app))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    
    application.run_polling()
