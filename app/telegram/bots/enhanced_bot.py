import logging
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, LabeledPrice
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, PreCheckoutQueryHandler,
    PollAnswerHandler, filters
)

# Import our custom API settings
try:
    from app.telegram.core.config import settings
except ImportError:
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

# Conversation states
SELECTING_ACTION, ADDING_TO_CART, CHECKOUT, PAYMENT, FEEDBACK = range(5)

# Payment provider token (replace with real token)
PAYMENT_PROVIDER_TOKEN = "YOUR_PAYMENT_PROVIDER_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start command with main menu."""
    keyboard = [
        [InlineKeyboardButton("Browse Products", callback_data='products')],
        [InlineKeyboardButton("View Cart", callback_data='cart')],
        [InlineKeyboardButton("My Orders", callback_data='orders')],
        [InlineKeyboardButton("Feedback Poll", callback_data='poll')],
        [InlineKeyboardButton("Web App Demo", web_app=WebAppInfo(url="https://python-telegram-bot.org/static/webappbot"))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to GroupMint! Choose an option:",
        reply_markup=reply_markup
    )
    return SELECTING_ACTION

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Browse products with inline keyboards."""
    query = update.callback_query
    await query.answer()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/products")
            products = response.json()
            if not products:
                await query.edit_message_text("No products available.")
                return SELECTING_ACTION
            
            text = "Available Products:\\n" + "\\n".join(
                f"{p.get('name', 'Unknown')} - ${p.get('price_cents', 0)/100:.2f}" for p in products[:10]
            )
            keyboard = [[InlineKeyboardButton(f"Add {p.get('name', 'Product')}", callback_data=f"add_to_cart_{p.get('id')}")] for p in products[:10]]
            keyboard.append([InlineKeyboardButton("Back", callback_data='back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            await query.edit_message_text("Error fetching products.")
    return ADDING_TO_CART

async def cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """View cart and proceed to checkout."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/cart?user_id={user_id}")
            cart_data = response.json()
            items = cart_data.get('items', [])
            if not items:
                await query.edit_message_text("Your cart is empty. Add some products first!")
                return SELECTING_ACTION
            
            text = f"Cart ({cart_data.get('total_items', 0)} items):\\n" + "\\n".join(
                f"{item['name']} x{item['quantity']}" for item in items
            )
            keyboard = [
                [InlineKeyboardButton("Proceed to Checkout", callback_data='checkout')],
                [InlineKeyboardButton("Back", callback_data='back')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error fetching cart: {e}")
            await query.edit_message_text("Error fetching cart.")
    return CHECKOUT

async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """View order history."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/orders?user_id={user_id}")
            orders = response.json()
            if not orders:
                await query.edit_message_text("No orders found.")
            else:
                text = "Your Orders:\\n" + "\\n".join(
                    f"Order {o['id']} - {o['status']}" for o in orders
                )
            keyboard = [[InlineKeyboardButton("Back", callback_data='back')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            await query.edit_message_text("Error fetching orders.")
    return SELECTING_ACTION

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Add product to cart."""
    query = update.callback_query
    product_id = query.data.split('_')[-1]
    user_id = str(update.effective_user.id)
    
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{API_BASE_URL}/cart/add?user_id={user_id}&product_id={product_id}&quantity=1")
            await query.answer("Added to cart!")
            # Return to products or cart view
            return await products(update, context)
        except Exception as e:
            logger.error(f"Error adding to cart: {e}")
            await query.edit_message_text("Error adding to cart.")
    return ADDING_TO_CART

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Initiate payment process."""
    query = update.callback_query
    await query.answer()
    
    # For demo, create a simple invoice
    chat_id = update.effective_chat.id
    title = "GroupMint Order"
    description = "Payment for your cart items"
    payload = "cart_checkout"
    currency = "USD"
    price = 10  # Example price in dollars
    prices = [LabeledPrice("Total", price * 100)]
    
    try:
        await context.bot.send_invoice(
            chat_id, title, description, payload, currency, prices,
            provider_token=PAYMENT_PROVIDER_TOKEN
        )
    except Exception as e:
        logger.error(f"Error sending invoice: {e}")
        await query.edit_message_text("Error processing payment.")
    return PAYMENT

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle pre-checkout."""
    query = update.pre_checkout_query
    if query.invoice_payload != "cart_checkout":
        await query.answer(ok=False, error_message="Invalid payload")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle successful payment."""
    await update.message.reply_text("Payment successful! Thank you for your purchase.")
    # Trigger order creation via API
    user_id = str(update.effective_user.id)
    async with httpx.AsyncClient() as client:
        await client.post(f"{API_BASE_URL}/orders/create?user_id={user_id}")

async def poll_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a feedback poll."""
    query = update.callback_query
    await query.answer()
    
    message = await context.bot.send_poll(
        update.effective_chat.id,
        "How satisfied are you with GroupMint?",
        ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied"],
        is_anonymous=False,
        allows_multiple_answers=False,
    )
    context.bot_data[message.poll.id] = {"chat_id": update.effective_chat.id}
    return FEEDBACK

async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle poll answers."""
    answer = update.poll_answer
    if answer.poll_id in context.bot_data:
        await context.bot.send_message(
            context.bot_data[answer.poll_id]["chat_id"],
            "Thank you for your feedback!"
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle all callbacks."""
    data = update.callback_query.data
    if data == 'back':
        return await start(update, context)
    elif data == 'products':
        return await products(update, context)
    elif data == 'cart':
        return await cart(update, context)
    elif data == 'orders':
        return await orders(update, context)
    elif data == 'poll':
        return await poll_feedback(update, context)
    elif data.startswith('add_to_cart_'):
        return await add_to_cart(update, context)
    elif data == 'checkout':
        return await checkout(update, context)
    return SELECTING_ACTION

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set a reminder timer."""
    try:
        minutes = int(context.args[0])
        if minutes < 0:
            await update.message.reply_text("Sorry, can't go back in time!")
            return
        context.job_queue.run_once(reminder, minutes * 60, chat_id=update.effective_chat.id, name=str(update.effective_chat.id), data="Order reminder!")
        await update.message.reply_text(f"Reminder set for {minutes} minutes.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /remind <minutes>")

async def reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the reminder message."""
    await context.bot.send_message(context.job.chat_id, text=f"Reminder: {context.job.data}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo messages."""
    await update.message.reply_text(update.message.text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error(f'Update {update} caused error {context.error}')
    if update and update.effective_chat:
        await context.bot.send_message(update.effective_chat.id, "An error occurred. Please try again.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION: [CallbackQueryHandler(handle_callback)],
            ADDING_TO_CART: [CallbackQueryHandler(handle_callback)],
            CHECKOUT: [CallbackQueryHandler(handle_callback)],
            PAYMENT: [PreCheckoutQueryHandler(precheckout_callback),
                      MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)],
            FEEDBACK: [PollAnswerHandler(receive_poll_answer)],
        },
        fallbacks=[CommandHandler('start', start)]
    )
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('remind', set_reminder))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_error_handler(error_handler)
    
    application.run_polling()
