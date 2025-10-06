import logging
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, PreCheckoutQueryHandler, MessageHandler, filters

# Import settings
try:
    from app.telegram.core.config import settings
except ImportError:
    settings = type('Settings', (), {
        'TELEGRAM_BOT_TOKEN': 'YOUR_BOT_TOKEN',
        'HOST': 'localhost',
        'PORT': 8000
    })()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

PAYMENT_PROVIDER_TOKEN = "YOUR_PAYMENT_PROVIDER_TOKEN"
API_BASE_URL = f"http://{settings.HOST}:{settings.PORT}/api/v1/telegram"

async def start_payment_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the payment bot with options."""
    keyboard = [
        [InlineKeyboardButton("Create Invoice", callback_data='invoice')],
        [InlineKeyboardButton("Check Status", callback_data='status')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Payment Bot - Choose an action:", reply_markup=reply_markup)

async def create_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create a payment invoice."""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    title = "GroupMint Payment"
    description = "Payment for services"
    payload = "payment_demo"
    currency = "USD"
    price = 5
    prices = [LabeledPrice("Service", price * 100)]
    
    try:
        await context.bot.send_invoice(
            chat_id, title, description, payload, currency, prices,
            provider_token=PAYMENT_PROVIDER_TOKEN
        )
    except Exception as e:
        logger.error(f"Error sending invoice: {e}")
        await query.edit_message_text("Error creating invoice.")

async def check_payment_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check payment status."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/payments/status/{user_id}")
            status = response.json().get('status', 'Unknown')
            await query.edit_message_text(f"Payment Status: {status}")
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            await query.edit_message_text("Error checking payment status.")

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle pre-checkout."""
    query = update.pre_checkout_query
    if query.invoice_payload == "payment_demo":
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Invalid payload")

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle successful payment."""
    await update.message.reply_text("Payment successful!")

if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start_payment_bot))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    
    application.run_polling()
