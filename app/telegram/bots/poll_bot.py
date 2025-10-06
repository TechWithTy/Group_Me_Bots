import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, PollAnswerHandler

# Import settings
try:
    from app.telegram.core.config import settings
except ImportError:
    settings = type('Settings', (), {
        'TELEGRAM_BOT_TOKEN': 'YOUR_BOT_TOKEN'
    })()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_poll_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a feedback poll."""
    message = await update.message.reply_poll(
        "How satisfied are you with our service?",
        ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied"],
        is_anonymous=False,
        allows_multiple_answers=False,
    )
    context.bot_data[message.poll.id] = {"chat_id": update.effective_chat.id}

async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle poll answers."""
    answer = update.poll_answer
    if answer.poll_id in context.bot_data:
        await context.bot.send_message(
            context.bot_data[answer.poll_id]["chat_id"],
            "Thank you for your feedback!"
        )

if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start_poll_bot))
    application.add_handler(PollAnswerHandler(receive_poll_answer))
    
    application.run_polling()
