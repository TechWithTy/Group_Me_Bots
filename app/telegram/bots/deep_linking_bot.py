import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

async def start_deep_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle deep linking."""
    payload = context.args[0] if context.args else ""
    if payload == "products":
        keyboard = [[InlineKeyboardButton("View Products", callback_data='products')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Deep link to products:", reply_markup=reply_markup)
    elif payload == "cart":
        await update.message.reply_text("Deep link to cart: Cart is empty.")
    else:
        await update.message.reply_text("Unknown deep link.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start_deep_link))
    
    application.run_polling()
