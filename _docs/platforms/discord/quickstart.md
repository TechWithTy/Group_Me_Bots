website=https://discordpy.readthedocs.io/en/stable/quickstart.html
Introduction

This is the documentation for discord.py, a library for Python to aid in creating applications that utilise the Discord API.
Prerequisites

discord.py works with Python 3.8 or higher. Support for earlier versions of Python is not provided. Python 2.7 or lower is not supported. Python 3.7 or lower is not supported.
Installing

You can get the library directly from PyPI:
content_copy

python3 -m pip install -U discord.py

If you are using Windows, then the following should be used instead:
content_copy

py -3 -m pip install -U discord.py

To get voice support, you should use discord.py[voice] instead of discord.py, e.g.
content_copy

python3 -m pip install -U discord.py[voice]

On Linux environments, installing voice requires getting the following dependencies:

    libffi

    libnacl

    python3-dev

For a Debian-based system, the following command will get these dependencies:
content_copy

$ apt install libffi-dev libnacl-dev python3-dev

Remember to check your permissions!
Virtual Environments

Sometimes you want to keep libraries from polluting system installs or use a different version of libraries than the ones installed on the system. You might also not have permissions to install libraries system-wide. For this purpose, the standard library as of Python 3.3 comes with a concept called “Virtual Environment”s to help maintain these separate versions.

A more in-depth tutorial is found on Virtual Environments and Packages.

However, for the quick and dirty:

    Go to your project’s working directory:

        content_copy

        $ cd your-bot-source
        $ python3 -m venv bot-env

    Activate the virtual environment:

        content_copy

        $ source bot-env/bin/activate

        On Windows you activate it with:
        content_copy

        $ bot-env\Scripts\activate.bat

    Use pip like usual:

        content_copy

        $ pip install -U discord.py

Congratulations. You now have a virtual environment all set up.

Scripts executed with py -3 will ignore any currently active virtual environment, as the -3 specifies a global scope.
Basic Concepts

discord.py revolves around the concept of events. An event is something you listen to and then respond to. For example, when a message happens, you will receive an event about it that you can respond to.

A quick example to showcase how events work:
content_copy

# This example requires the 'message_content' intent.

import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run('my token goes here')

