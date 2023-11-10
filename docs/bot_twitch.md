# TwitchBot Documentation

## Overview

`bot_twitch.py` is a Twitch bot designed to check if a channel is live or not. It utilizes the Twitch API to determine the channel's live status and provides various chat commands for interaction.

### About

This script introduces a `TwitchBot` class that extends the `commands.Bot` class from the `twitchio` library. It also utilizes several modules for handling authentication, channels, commands, events, and streams. The bot interacts with the Luna API for translation and question-answering tasks.

## Class: `TwitchBot`

### Initialization

```python
def __init__(self, config: dict, logger: ValkyrieLogger, task_queue: TaskQueue):
    """
    Initializes the TwitchBot class.

    Args:
        config (dict): The configuration dictionary.
        logger (ValkyrieLogger): The logger.
        task_queue (TaskQueue): The queue instance.
    """
```

### Attributes

- `loaded`: Indicates whether the bot is loaded.
- `running`: Indicates whether the bot is running.
- `logger`: The logger instance.
- `config`: The configuration dictionary.
- `task_queue`: The TaskQueue instance for managing tasks.
- `stream`: Instance of the Stream class for handling stream-related tasks.
- `channel`: Instance of the Channel class for handling channel-related tasks.
- `auth`: Instance of the Auth class for handling Twitch authentication.
- `luna`: Instance of the Luna class for Luna API interactions.
- `scopes`: List of Twitch authentication scopes.
- `user_token`: User token obtained during authentication.
- `bot_token`: Bot token obtained during authentication.
- `pubsub`: PubSubPool instance for handling PubSub events.
- `event_handler`: Instance of the Event class for handling Twitch events.
- `cmd_handler`: Instance of the Commands class for handling chat commands.
- `start_time`: Timestamp indicating the bot's start time.

### Events

- `event_ready`: Triggered when the bot goes online.
- `event_pubsub_bits`: Triggered when a user cheers with bits.
- `event_pubsub_channel_points`: Triggered when a user redeems a channel point reward.
- `event_pubsub_channel_subscriptions`: Triggered when a user subscribes to the channel.

### Commands

- `tw_ping`: Command to check the bot's latency.
- `tw_discord`: Command to get the Discord invite link.
- `tw_exval`: Command to get the ExVal Limited link.
- `tw_translate`: Command to translate text using Luna.
- `tw_ask`: Command to ask Luna a question.
- `tw_set_title`: Mod-only command to set the stream title.
- `tw_set_game`: Mod-only command to set the stream game.
- `tw_design_doc`: Command to get the game design document.
- `tw_manual_doc`: Command to get the game manual document.

## Dependencies

- [ValkyrieUtils](https://github.com/ValkyFischer/ValkyrieUtils): Utilities library for the ***0xLUN4*** project.
- [tasks](modules/tasks.md): Custom module for managing tasks.
- [luna](modules/luna.md): Custom module for managing tasks.
- [time](https://docs.python.org/3/library/time.html): Module for time-related functions.
- [twitchio](https://twitchio.dev/en/stable/): TwitchIO commands extension.
- [Twitch.auth](twitch/auth.md): Custom module for handling Twitch authentication.
- [Twitch.channel](twitch/channel.md): Custom module for handling Twitch channels.
- [Twitch.commands](twitch/commands.md): Custom module for handling Twitch chat commands.
- [Twitch.events](twitch/events.md): Custom module for handling Twitch events.
- [Twitch.stream](twitch/stream.md): Custom module for handling Twitch streams.

## Configuration

The TwitchBot class relies on configuration settings provided in the overall project configuration dictionary.

## Usage

To use the Twitch bot, create an instance of the `TwitchBot` class and handle events and commands as needed.

Example:

```python
from bot_twitch import TwitchBot

# Create a TwitchBot instance
twitch_bot = TwitchBot(config, logger, task_queue)

# Start the bot
twitch_bot.run()
```