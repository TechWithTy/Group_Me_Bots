import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

# Import settings
try:
    from app.telegram.core.config import settings
except ImportError:
    settings = type('Settings', (), {
        'TELEGRAM_BOT_TOKEN': 'YOUR_BOT_TOKEN'
    })()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

SELECTING_FEATURE, TYPING = range(2)

async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start conversation."""
    keyboard = [
        [InlineKeyboardButton("Feature A", callback_data='feature_a')],
        [InlineKeyboardButton("Feature B", callback_data='feature_b')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a feature:", reply_markup=reply_markup)
    return SELECTING_FEATURE

async def select_feature(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Select feature and ask for input."""
    query = update.callback_query
    await query.answer()
    context.user_data['feature'] = query.data
    await query.edit_message_text(f"You selected {query.data}. Tell me more:")
    return TYPING

async def save_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save user input."""
    feature = context.user_data.get('feature')
    user_input = update.message.text
    await update.message.reply_text(f"Feature {feature}: {user_input}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation."""
    await update.message.reply_text("Conversation cancelled.")
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_conversation)],
        states={
            SELECTING_FEATURE: [CallbackQueryHandler(select_feature)],
            TYPING: [MessageHandler(filters.TEXT, save_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler)
    
    application.run_polling()
