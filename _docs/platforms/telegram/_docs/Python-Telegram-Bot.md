https://docs.python-telegram-bot.org/en/stable/
https://github.com/python-telegram-bot/python-telegram-bot
python-telegram-bot Logo PyPi Package Version Supported Python versions Supported Bot API version PyPi Package Monthly Download Documentation Status LGPLv3 License Github Actions workflow Code coverage Median time to resolve an issue Code quality: Codacy pre-commit.ci status Code Style: Black Telegram Channel Telegram Group

We have made you a wrapper you can’t refuse

We have a vibrant community of developers helping each other in our Telegram group. Join us!

Stay tuned for library updates and new releases on our Telegram Channel.
Introduction

This library provides a pure Python, asynchronous interface for the Telegram Bot API. It’s compatible with Python versions 3.9+.

In addition to the pure API implementation, this library features several convenience methods and shortcuts as well as a number of high-level classes to make the development of bots easy and straightforward. These classes are contained in the telegram.ext submodule.

After installing the library, be sure to check out the section on working with PTB.
Telegram API support

All types and methods of the Telegram Bot API 9.2 are natively supported by this library. In addition, Bot API functionality not yet natively included can still be used as described in our wiki.
Notable Features

    Fully asynchronous

    Convenient shortcut methods, e.g. Message.reply_text

    Fully annotated with static type hints

    Customizable and extendable interface

    Seamless integration with webhooks and polling

    Comprehensive documentation and examples

Installing

You can install or upgrade python-telegram-bot via

$ pip install python-telegram-bot --upgrade

To install a pre-release, use the --pre flag in addition.

You can also install python-telegram-bot from source, though this is usually not necessary.

$ git clone https://github.com/python-telegram-bot/python-telegram-bot
$ cd python-telegram-bot
$ pip install build
$ python -m build

You can also use your favored package manager (such as uv, hatch, poetry, etc.) instead of pip.
Verifying Releases

To enable you to verify that a release file that you downloaded was indeed provided by the python-telegram-bot team, we have taken the following measures.

Starting with v21.4, all releases are signed via sigstore. The corresponding signature files are uploaded to the GitHub releases page. To verify the signature, please install the sigstore Python client and follow the instructions for verifying signatures from GitHub Actions. As input for the --repository parameter, please use the value python-telegram-bot/python-telegram-bot.

Earlier releases are signed with a GPG key. The signatures are uploaded to both the GitHub releases page and the PyPI project and end with a suffix .asc. Please find the public keys here. The keys are named in the format <first_version>-<last_version>.gpg.

In addition, the GitHub release page also contains the sha1 hashes of the release files in the files with the suffix .sha1.
Dependencies & Their Versions

python-telegram-bot tries to use as few 3rd party dependencies as possible. However, for some features using a 3rd party library is more sane than implementing the functionality again. As these features are optional, the corresponding 3rd party dependencies are not installed by default. Instead, they are listed as optional dependencies. This allows to avoid unnecessary dependency conflicts for users who don’t need the optional features.

The only required dependency is httpx >=0.27,<0.29 for telegram.request.HTTPXRequest, the default networking backend.

python-telegram-bot is most useful when used along with additional libraries. To minimize dependency conflicts, we try to be liberal in terms of version requirements on the (optional) dependencies. On the other hand, we have to ensure stability of python-telegram-bot, which is why we do apply version bounds. If you encounter dependency conflicts due to these bounds, feel free to reach out.
Optional Dependencies

PTB can be installed with optional dependencies:

    pip install "python-telegram-bot[passport]" installs the cryptography>=39.0.1 library. Use this, if you want to use Telegram Passport related functionality.

    pip install "python-telegram-bot[socks]" installs httpx[socks]. Use this, if you want to work behind a Socks5 server.

    pip install "python-telegram-bot[http2]" installs httpx[http2]. Use this, if you want to use HTTP/2.

    pip install "python-telegram-bot[rate-limiter]" installs aiolimiter~=1.1,<1.3. Use this, if you want to use telegram.ext.AIORateLimiter.

    pip install "python-telegram-bot[webhooks]" installs the tornado~=6.4 library. Use this, if you want to use telegram.ext.Updater.start_webhook/telegram.ext.Application.run_webhook.

    pip install "python-telegram-bot[callback-data]" installs the cachetools>=5.3.3,<6.3.0 library. Use this, if you want to use arbitrary callback_data.

    pip install "python-telegram-bot[job-queue]" installs the APScheduler>=3.10.4,<3.12.0 library. Use this, if you want to use the telegram.ext.JobQueue.

To install multiple optional dependencies, separate them by commas, e.g. pip install "python-telegram-bot[socks,webhooks]".

Additionally, two shortcuts are provided:

    pip install "python-telegram-bot[all]" installs all optional dependencies.

    pip install "python-telegram-bot[ext]" installs all optional dependencies that are related to telegram.ext, i.e. [rate-limiter, webhooks, callback-data, job-queue].

Working with PTB

Once you have installed the library, you can begin working with it - so let’s get started!
Quick Start

Our Wiki contains an Introduction to the API explaining how the pure Bot API can be accessed via python-telegram-bot. Moreover, the Tutorial: Your first Bot gives an introduction on how chatbots can be easily programmed with the help of the telegram.ext module.
Resources

    The package documentation is the technical reference for python-telegram-bot. It contains descriptions of all available classes, modules, methods and arguments as well as the changelog.

    The wiki is home to number of more elaborate introductions of the different features of python-telegram-bot and other useful resources that go beyond the technical documentation.

    Our examples section contains several examples that showcase the different features of both the Bot API and python-telegram-bot. Even if it is not your approach for learning, please take a look at echobot.py. It is the de facto base for most of the bots out there. The code for these examples is released to the public domain, so you can start by grabbing the code and building on top of it.

    The official Telegram Bot API documentation is of course always worth a read.

Getting help

If the resources mentioned above don’t answer your questions or simply overwhelm you, there are several ways of getting help.

    We have a vibrant community of developers helping each other in our Telegram group. Join us! Asking a question here is often the quickest way to get a pointer in the right direction.

    Ask questions by opening a discussion.

    You can even ask for help on Stack Overflow using the python-telegram-bot tag.

Concurrency

Since v20.0, python-telegram-bot is built on top of Pythons asyncio module. Because asyncio is in general single-threaded, python-telegram-bot currently does not aim to be thread-safe. Noteworthy parts of python-telegram-bots API that are likely to cause issues (e.g. race conditions) when used in a multi-threaded setting include:

    telegram.ext.Application/Updater.update_queue

    telegram.ext.ConversationHandler.check/handle_update

    telegram.ext.CallbackDataCache

    telegram.ext.BasePersistence

    all classes in the telegram.ext.filters module that allow to add/remove allowed users/chats at runtime

Contributing

Contributions of all sizes are welcome. Please review our contribution guidelines to get started. You can also help by reporting bugs or feature requests.
Donating

Occasionally we are asked if we accept donations to support the development. While we appreciate the thought, maintaining PTB is our hobby, and we have almost no running costs for it. We therefore have nothing set up to accept donations. If you still want to donate, we kindly ask you to donate to another open source project/initiative of your choice instead.
License
You may copy, distribute and modify the software provided that modifications are described and licensed for free under LGPL-3. Derivative works (including modifications or anything statically linked to the library) can only be redistributed under LGPL-3, but applications that use the library don’t have to be.