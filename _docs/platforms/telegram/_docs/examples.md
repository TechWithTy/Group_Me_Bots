Examples

In this section we display small examples to show what a bot written with python-telegram-bot looks like. Some bots focus on one specific aspect of the Telegram Bot API while others focus on one of the mechanics of this library. Except for the rawapibot.py example, they all use the high-level framework this library provides with the telegram.ext submodule.

All examples are licensed under the CC0 License and are therefore fully dedicated to the public domain. You can use them as the base for your own bots without worrying about copyrights.

Do note that we ignore one pythonic convention. Best practice would dictate, in many handler callbacks function signatures, to replace the argument context with an underscore, since context is an unused local variable in those callbacks. However, since these are examples and not having a name for that argument confuses beginners, we decided to have it present.
echobot.py

This is probably the base for most of the bots made with python-telegram-bot. It simply replies to each text message with a message that contains the same text.
timerbot.py

This bot uses the telegram.ext.JobQueue class to send timed messages. The user sets a timer by using /set command with a specific time, for example /set 30. The bot then sets up a job to send a message to that user after 30 seconds. The user can also cancel the timer by sending /unset. To learn more about the JobQueue, read this wiki article. Note: To use JobQueue, you must install PTB via pip install "python-telegram-bot[job-queue]"
conversationbot.py

A common task for a bot is to ask information from the user. In v5.0 of this library, we introduced the telegram.ext.ConversationHandler for that exact purpose. This example uses it to retrieve user-information in a conversation-like style. To get a better understanding, take a look at the state diagram.
conversationbot2.py

A more complex example of a bot that uses the ConversationHandler. It is also more confusing. Good thing there is a fancy state diagram. for this one, too!
nestedconversationbot.py

An even more complex example of a bot that uses the nested ConversationHandlers. While it’s certainly not that complex that you couldn’t built it without nested ConversationHanldlers, it gives a good impression on how to work with them. Of course, there is a fancy state diagram for this example, too!
persistentconversationbot.py

A basic example of a bot store conversation state and user_data over multiple restarts.
inlinekeyboard.py

This example sheds some light on inline keyboards, callback queries and message editing. A wiki site explaining this examples lives here.
inlinekeyboard2.py

A more complex example about inline keyboards, callback queries and message editing. This example showcases how an interactive menu could be build using inline keyboards.
deeplinking.py

A basic example on how to use deeplinking with inline keyboards.
inlinebot.py

A basic example of an inline bot. Don’t forget to enable inline mode with @BotFather.
pollbot.py

This example sheds some light on polls, poll answers and the corresponding handlers.
passportbot.py

A basic example of a bot that can accept passports. Use in combination with the HTML page. Don’t forget to enable and configure payments with @BotFather. Check out this guide on Telegram passports in PTB. Note: To use Telegram Passport, you must install PTB via pip install "python-telegram-bot[passport]"
paymentbot.py

A basic example of a bot that can accept payments. Don’t forget to enable and configure payments with @BotFather.
errorhandlerbot.py

A basic example on how to set up a custom error handler.
chatmemberbot.py

A basic example on how (my_)chat_member updates can be used.
webappbot.py

A basic example of how Telegram WebApps can be used. Use in combination with the HTML page. For your convenience, this file is hosted by the PTB team such that you don’t need to host it yourself. Uses the iro.js JavaScript library to showcase a user interface that is hard to achieve with native Telegram functionality.
contexttypesbot.py

This example showcases how telegram.ext.ContextTypes can be used to customize the context argument of handler and job callbacks.
customwebhookbot.py

This example showcases how a custom webhook setup can be used in combination with telegram.ext.Application.
arbitrarycallbackdatabot.py

This example showcases how PTBs “arbitrary callback data” feature can be used. Note: To use arbitrary callback data, you must install PTB via pip install "python-telegram-bot[callback-data]"
Pure API
The rawapibot.py example example uses only the pure, “bare-metal” API wrapper.https://docs.python-telegram-bot.org/en/stable/examples.rawapibot.html

rawapibot.py

This example uses only the pure, “bare-metal” API wrapper.

#!/usr/bin/env python

"""Simple Bot to reply to Telegram messages.


This is built on the API wrapper, see echobot.py to see the same example built

on the telegram.ext bot framework.

This program is dedicated to the public domain under the CC0 license.

"""


import asyncio

import contextlib

import datetime as dtm

import logging

from typing import NoReturn


from telegram import Bot, Update

from telegram.error import Forbidden, NetworkError


logging.basicConfig(

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO

)

# set higher logging level for httpx to avoid all GET and POST requests being logged

logging.getLogger("httpx").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)



async def main() -> NoReturn:

    """Run the bot."""

    # Here we use the `async with` syntax to properly initialize and shutdown resources.

    async with Bot("TOKEN") as bot:

        # get the first pending update_id, this is so we can skip over it in case

        # we get a "Forbidden" exception.

        try:

            update_id = (await bot.get_updates())[0].update_id

        except IndexError:

            update_id = None


        logger.info("listening for new messages...")

        while True:

            try:

                update_id = await echo(bot, update_id)

            except NetworkError:

                await asyncio.sleep(1)

            except Forbidden:

                # The user has removed or blocked the bot.

                update_id += 1



async def echo(bot: Bot, update_id: int) -> int:

    """Echo the message the user sent."""

    # Request updates after the last update_id

    updates = await bot.get_updates(

        offset=update_id, timeout=dtm.timedelta(seconds=10), allowed_updates=Update.ALL_TYPES

    )

    for update in updates:

        next_update_id = update.update_id + 1


        # your bot can receive updates without messages

        # and not all messages contain text

        if update.message and update.message.text:

            # Reply to the message

            logger.info("Found message %s!", update.message.text)

            await update.message.reply_text(update.message.text)

        return next_update_id

    return update_id



if __name__ == "__main__":

    with contextlib.suppress(KeyboardInterrupt):  # Ignore exception when Ctrl-C is pressed

        asyncio.run(main())

