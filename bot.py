import logging
import asyncio
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Import our custom API settings
try:
    from app.telegram.core.config import settings
except ImportError:
    # Fallback if config not available
    settings = type('Settings', (), {
        'TELEGRAM_BOT_TOKEN': 'YOUR_BOT_TOKEN',
        'DEBUG': True,
        'HOST': 'localhost',
        'PORT': 8000
    })()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Base URL for our custom API
API_BASE_URL = f"http://{settings.HOST}:{settings.PORT}/api/v1/telegram"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    keyboard = [
        [InlineKeyboardButton("Browse Products", callback_data='products')],
        [InlineKeyboardButton("View Cart", callback_data='cart')],
        [InlineKeyboardButton("My Orders", callback_data='orders')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to GroupMint! Choose an option:",
        reply_markup=reply_markup
    )

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle products command or callback."""
    query = update.callback_query
    if query:
        await query.answer()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/products")
            products = response.json()
            if not products:
                text = "No products available."
            else:
                text = "Available Products:\\n" + "\\n".join(
                    f"{p.get('name', 'Unknown')} - ${p.get('price_cents', 0)/100:.2f}" for p in products[:5]
                )
                keyboard = [[InlineKeyboardButton(f"Add {p.get('name', 'Product')}", callback_data=f"add_to_cart_{p.get('id')}")] for p in products[:5]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await (query.message.reply_text if query else update.message.reply_text)(text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            await (query.message.reply_text if query else update.message.reply_text)("Error fetching products.")

async def cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cart view."""
    query = update.callback_query
    if query:
        await query.answer()
    
    # For demo, assume user_id from update
    user_id = str(update.effective_user.id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/cart?user_id={user_id}")
            cart_data = response.json()
            items = cart_data.get('items', [])
            if not items:
                text = "Your cart is empty."
            else:
                text = f"Cart ({cart_data.get('total_items', 0)} items):\\n" + "\\n".join(
                    f"{item['name']} x{item['quantity']}" for item in items
                )
                keyboard = [[InlineKeyboardButton("Checkout", callback_data='checkout')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await (query.message.reply_text if query else update.message.reply_text)(text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error fetching cart: {e}")
            await (query.message.reply_text if query else update.message.reply_text)("Error fetching cart.")

async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle orders view."""
    query = update.callback_query
    if query:
        await query.answer()
    
    user_id = str(update.effective_user.id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/orders?user_id={user_id}")
            orders = response.json()
            if not orders:
                text = "No orders found."
            else:
                text = "Your Orders:\\n" + "\\n".join(
                    f"Order {o['id']} - {o['status']}" for o in orders
                )
                await (query.message.reply_text if query else update.message.reply_text)(text)
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            await (query.message.reply_text if query else update.message.reply_text)("Error fetching orders.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks."""
    query = update.callback_query
    data = query.data
    if data.startswith('add_to_cart_'):
        product_id = data.split('_')[-1]
        user_id = str(update.effective_user.id)
        async with httpx.AsyncClient() as client:
            try:
                await client.post(f"{API_BASE_URL}/cart/add?user_id={user_id}&product_id={product_id}&quantity=1")
                await query.edit_message_text("Item added to cart!")
            except Exception as e:
                logger.error(f"Error adding to cart: {e}")
                await query.edit_message_text("Error adding to cart.")
    elif data == 'checkout':
        await query.edit_message_text("Checkout feature coming soon!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo any text message."""
    await update.message.reply_text(update.message.text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    # Build application
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Run bot
    application.run_polling()
