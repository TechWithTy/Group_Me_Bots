import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler

# Import settings
try:
    from app.telegram.core.config import settings
except ImportError:
    settings = type('Settings', (), {
        'TELEGRAM_BOT_TOKEN': 'YOUR_BOT_TOKEN'
    })()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

SELECTING_LEVEL, SELECTING_OPTION = range(2)

async def start_nested(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start nested conversation."""
    keyboard = [
        [InlineKeyboardButton("Level 1", callback_data='level_1')],
        [InlineKeyboardButton("Level 2", callback_data='level_2')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a level:", reply_markup=reply_markup)
    return SELECTING_LEVEL

async def select_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Select level and show options."""
    query = update.callback_query
    await query.answer()
    level = query.data
    keyboard = [
        [InlineKeyboardButton(f"Option A for {level}", callback_data=f'option_a_{level}')],
        [InlineKeyboardButton(f"Option B for {level}", callback_data=f'option_b_{level}')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"Options for {level}:", reply_markup=reply_markup)
    return SELECTING_OPTION

async def select_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle option selection."""
    query = update.callback_query
    await query.answer()
    option = query.data
    await query.edit_message_text(f"You selected {option}. Conversation ended.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation."""
    await update.message.reply_text("Conversation cancelled.")
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_nested)],
        states={
            SELECTING_LEVEL: [CallbackQueryHandler(select_level)],
            SELECTING_OPTION: [CallbackQueryHandler(select_option)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler)
    
    application.run_polling()
