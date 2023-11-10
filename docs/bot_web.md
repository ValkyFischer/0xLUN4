# WebServer Documentation

## Overview

`bot_web.py` is a Python script that implements a web management system for various bots, including Twitch and Discord, within the Valkyrie Bot project.

### About

This script initializes a Flask web server to manage the Valkyrie Bot and its associated components. It provides web-based interfaces to monitor and control the Valkyrie Bot, Twitch bot, and Discord bot.

## Class: `WebServer`

```python
def __init__(self, twitch_b, discord_b, valky_b, logger, config, valky):
      """
      Initializes the WebServer class.

      Args:
          twitch_b: Instance of the Twitch bot class.
          discord_b: Instance of the Discord bot class.
          valky_b: Instance of the Valkyrie bot class.
          logger: The logger instance.
          config: Configuration settings.
          valky: Valkyrie instance.
      """
```

### Attributes

- `config`: Configuration settings.
- `logger`: The logger instance.
- `valky`: Valkyrie instance.
- `build`: Version information encoded in hexadecimal format.
- `build_v`: Version information split and formatted.
- `luna`: Instance of the Luna class.
- `luna_time`: Timestamp for tracking the last Luna API ping.
- `luna_ping`: Latency of the Luna API.
- `luna_interval`: Interval for pinging the Luna API, defined in the configuration file.
- `tw_bot`: Instance of the TwitchBot class.
- `dc_bot`: Instance of the DiscordBot class.
- `vk_bot`: Instance of the ValkyrieBot class.
- `app`: Flask application instance.
- `loop`: Event loop for asynchronous tasks.

### Methods

- `setup(self)`: Sets up the web server with various routes and functions.
- `index(self, lang='en')`: Renders the index page with an overview of bot statuses.
- `logs(self, lang='en')`: Renders the logs page with the latest log entries.
- `valky_bot(self, lang='en')`: Renders the Valkyrie bot page with status and recent tasks.
- `valky_settings(self, lang='en')`: Renders the Valkyrie bot settings page.
- `valky_luna(self, lang='en')`: Renders the Valkyrie bot Luna page.
- `valky_tasks(self, lang='en')`: Renders the Valkyrie bot tasks page.
- `valky_tasks_new(self, lang='en')`: Renders the Valkyrie bot new tasks page.
- `twitch_bot(self, lang='en')`: Renders the Twitch bot page with status and stream information.
- `twitch_settings(self, lang='en')`: Renders the Twitch bot settings page.
- `valky_tasks_post(self, lang='en')`: Handles the creation of new tasks.
- `valky_tasks_action(self, task_id, action, lang='en')`: Handles actions on existing tasks.
- `login(self)`: Handles user login.
- `logout(self)`: Handles user logout.
- `start_bot(self, bot)`: Starts a specified bot.
- `start_vk_bot(self)`: Starts the Valkyrie bot.
- `start_dc_bot(self)`: Starts the Discord bot.
- `start_tw_bot(self)`: Starts the Twitch bot.
- `getLogs(self)`: Retrieves the latest log entries.
- `getTasks(self)`: Retrieves task-related information.

### Dependencies

- [ValkyrieUtils](https://github.com/ValkyFischer/ValkyrieUtils): Utilities library for the ***0xLUN4*** project.
- [tasks](modules/tasks.md): Custom module for managing tasks.
- [luna](modules/luna.md): Custom module for managing tasks.
- [flask](https://flask.palletsprojects.com/en/2.0.x/): A lightweight WSGI web application framework.
- [requests](https://docs.python-requests.org/en/master/): A simple HTTP library for Python.
- [waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/): A production-quality pure-Python WSGI server.
- [threading](https://docs.python.org/3/library/threading.html): Module for managing threads.
- [time](https://docs.python.org/3/library/time.html): Module for time-related functions.
- [binascii](https://docs.python.org/3/library/binascii.html): Module for converting between binary and ASCII.

## Usage

To use the `WebServer` class, create an instance and call its `run` method.

Example:

```python
from bot_web import WebServer
from bot_discord import DiscordBot
from bot_twitch import TwitchBot
from bot_valkyrie import ValkyrieBot

# Create instances of DiscordBot, TwitchBot, and ValkyrieBot
discord_bot = DiscordBot(config, logger, task_queue)
twitch_bot = TwitchBot(config, logger, task_queue)
valkyrie_bot = ValkyrieBot(twitch_bot, discord_bot, config, logger, task_queue)

# Create WebServer instance
web_server = WebServer(twitch_bot, discord_bot, valkyrie_bot, logger, config, valkyrie)

# Run the WebServer
web_server.run(loop)
```
