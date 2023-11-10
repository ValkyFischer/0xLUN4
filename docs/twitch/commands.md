# Twitch.commands Documentation

## Overview

`Twitch/commands.py` provides functionality to serve commands to the Twitch bot. This script defines a `Commands` class with various methods representing different commands that the bot can respond to.

### About

This script serves as the command handler for the Twitch bot, allowing users to interact with the bot through specific commands.

## Class: `Commands`

### Initialization

```python
def __init__(self, bot):
    """
    Initializes the Commands class.

    Args:
        bot: The Twitch bot instance.
    """
```

### Methods

#### `do_ping(self, ctx: commands.Context) -> None`

- A command that can be used to check the latency of the bot.

  - Args:
    - `ctx` (commands.Context): The context of the command.

#### `do_discord(self, ctx: commands.Context) -> None`

- A command that can be used to get the Discord invite link.

  - Args:
    - `ctx` (commands.Context): The context of the command.

#### `do_exval(self, ctx: commands.Context) -> None`

- A command that can be used to get the ExVal Limited link.

  - Args:
    - `ctx` (commands.Context): The context of the command.

#### `do_translate(self, ctx: commands.Context, text: str) -> None`

- A command that can be used to translate text using Luna.

  - Args:
    - `ctx` (commands.Context): The context of the command.
    - `text` (str): The text to translate.

#### `do_ask(self, ctx: commands.Context, text: str) -> None`

- A command that can be used to ask Luna a question.

  - Args:
    - `ctx` (commands.Context): The context of the command.
    - `text` (str): The question to ask.

#### `do_set_title(self, ctx: commands.Context, title: str) -> None`

- A command that can be used to set the title of the stream.

  - Args:
    - `ctx` (commands.Context): The context of the command.
    - `title` (str): The title of the stream.

#### `do_set_game(self, ctx: commands.Context, game: str) -> None`

- A command that can be used to set the game of the stream.

  - Args:
    - `ctx` (commands.Context): The context of the command.
    - `game` (str): The game of the stream.

#### `do_design_doc(self, ctx: commands.Context) -> None`

- A command that can be used to get the design document.

  - Args:
    - `ctx` (commands.Context): The context of the command.

#### `do_manual_doc(self, ctx: commands.Context) -> None`

- A command that can be used to get the manual document.

  - Args:
    - `ctx` (commands.Context): The context of the command.

## Dependencies

- [random](https://docs.python.org/3/library/random.html): Standard Python random module.
- [twitchio](https://twitchio.dev/en/stable/): TwitchIO commands extension.

## Usage

To use the `Commands` class, create an instance, and TwitchIO will automatically route incoming commands to the appropriate method.

Example:

```python
from Twitch.commands import Commands

# Create a Commands instance
twitch_commands = Commands(bot_instance)

# TwitchIO will automatically route commands to the appropriate method
```