import asyncio
import contextlib
import logging
from typing import NoReturn
from telegram import Bot, Update
from telegram.error import Forbidden, NetworkError

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def main() -> NoReturn:
    """Run the bot using raw API."""
    async with Bot("YOUR_BOT_TOKEN") as bot:
        update_id = None
        logger.info("Listening for messages...")
        while True:
            try:
                update_id = await echo(bot, update_id)
            except NetworkError:
                await asyncio.sleep(1)
            except Forbidden:
                update_id += 1

async def echo(bot: Bot, update_id: int) -> int:
    """Echo messages."""
    updates = await bot.get_updates(offset=update_id, timeout=10, allowed_updates=Update.ALL_TYPES)
    for update in updates:
        next_update_id = update.update_id + 1
        if update.message and update.message.text:
            logger.info(f"Found message: {update.message.text}")
            await update.message.reply_text(update.message.text)
        return next_update_id
    return update_id

if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
