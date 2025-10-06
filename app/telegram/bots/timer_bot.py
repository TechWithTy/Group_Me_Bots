import logging
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

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set a reminder timer."""
    try:
        minutes = int(context.args[0])
        if minutes < 0:
            await update.message.reply_text("Sorry, can't go back in time!")
            return
        context.job_queue.run_once(reminder, minutes * 60, chat_id=update.effective_chat.id, name=str(update.effective_chat.id), data="Timer reminder!")
        await update.message.reply_text(f"Timer set for {minutes} minutes.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /set <minutes>")

async def reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the reminder message."""
    await context.bot.send_message(context.job.chat_id, text=f"Reminder: {context.job.data}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('set', set_timer))
    
    application.run_polling()
