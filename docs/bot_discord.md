# DiscordBot Documentation

## Overview

`bot_discord.py` is a Discord bot designed for sending notifications to a Discord server. The bot utilizes the Discord API for sending notifications and implementing slash commands. Additionally, it employs the Twitch API to determine if a channel is live or offline, sending Discord notifications accordingly.

### About

The script initializes the Discord bot, sets up the necessary components, and defines commands that users can interact with on the Discord server.

## Class: `DiscordBot`

```python
def __init__(self, config: dict, logger: ValkyrieLogger, task_queue: TaskQueue):
    """
    Initializes the DiscordBot class.

    Args:
        config (dict): The configuration dictionary.
        logger (ValkyrieLogger): The logger.
        task_queue (TaskQueue): The queue.
    """
```

### Attributes

- `loaded`: Indicates whether the bot is loaded.
- `running`: Indicates whether the bot is running.
- `logger`: The logger instance.
- `config`: The configuration dictionary.
- `task_queue`: The TaskQueue instance for managing tasks.
- `token`: The Discord bot token.
- `guild_id`: The Discord guild ID.
- `activity`: The Discord bot activity.
- `intents`: Discord Intents for controlling the bot's event subscriptions.
- `client`: The Discord bot client instance.
- `tree`: CommandTree instance for managing slash commands.
- `guild`: The Discord guild object.
- `ch_admin`, `ch_cmd`, `ch_stream`: Discord channel objects for admin, command, and stream channels.
- `start_time`: Timestamp indicating the bot's start time.

### Methods

#### `setup(self)`
- Sets up the Discord bot, including adding slash commands and setting up the `on_ready` event.

#### `send_log(self, message: str)`
- Sends a message to the admin channel, formatted with a [LOG] prefix.
  - Args:
    - `message` (str): The message to send.

#### `send_notification(self, channel: str)`
- Sends a message to the stream channel, formatted as an embed message.
  - Args:
    - `channel` (str): The channel name.

#### `assign_role(self, user_id: int | str, role: str)`
- Assigns a role to a user.
  - Args:
    - `user_id` (int | str): The user id of the user.
    - `role` (str): The role to assign.

### Modal Classes

#### `LunaSupport`
- Discord modal for opening a support ticket.

#### `LunaTranslate`
- Discord modal for translating text into English.

#### `LunaAsk`
- Discord modal for asking L.U.N.A. a question.

## Dependencies

- [ValkyrieUtils](https://github.com/ValkyFischer/ValkyrieUtils): Utilities library for the ***0xLUN4*** project.
- [tasks](modules/tasks.md): Custom module for managing tasks.
- [luna](modules/luna.md): Custom module for managing tasks.
- [discord](https://discordpy.readthedocs.io/en/stable/): Discord API wrapper for Python.
- [datetime](https://docs.python.org/3/library/datetime.html): Standard Python datetime module.
- [os](https://docs.python.org/3/library/os.html): Module for interacting with the operating system.

## Usage

To use the `DiscordBot` class, create an instance and call its methods to interact with Discord server commands.

Example:

```python
from Discord.bot_discord import DiscordBot

# Create DiscordBot instance
discord_bot = DiscordBot(config, logger, task_queue)

# Set up the Discord bot
discord_bot.setup()

# Interact with the bot using commands
```
