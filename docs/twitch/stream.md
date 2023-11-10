# Twitch.stream Documentation

## Overview

`Twitch/stream.py` provides functionality to set and get information about a Twitch stream and game. The script defines two classes, `Stream` and `Game`, each with specific properties and methods for managing stream-related information.

### About

This script is responsible for interacting with the Twitch API to retrieve and update information related to a Twitch channel's stream and the game being played.

## Class: `Stream`

```python
def __init__(self, config: dict, logger: ValkyrieLogger):
    """
    Initializes the Stream class.

    Args:
        config (dict): The configuration dictionary.
        logger (ValkyrieLogger): The logger.
    """
```

### Methods

#### `get_info(self, user_id: int) -> dict`

- Gets the information of a channel.

  - Args:
    - `user_id` (int): The user id of the channel.

  - Returns:
    - dict: A dictionary of information.

#### `set_info(self, user_id: int, title: str = None, game_name: str = None, language: str = None, tags: list = None) -> bool`

- Sets the information of a channel.

  - Args:
    - `user_id` (int): The user id of the channel.
    - `title` (str): The title of the stream.
    - `game_name` (str): The name of the game used to get the game id.
    - `language` (str): The language of the stream.
    - `tags` (list): A list of tags.

  - Returns:
    - bool: True if the information was set, False if the information was not set.

## Class: `Game`

```python
def __init__(self, config: dict, logger: ValkyrieLogger):
    """
    Initializes the Game class.

    Args:
        config (dict): The configuration dictionary.
        logger (ValkyrieLogger): The logger.
    """
```

### Methods

#### `get_id(self, name: str) -> int`

- Gets the game id from the game name.

  - Args:
    - `name` (str): The name of the game.

  - Returns:
    - int: The id of the game.

## Dependencies

- [ValkyrieUtils](https://github.com/ValkyFischer/ValkyrieUtils): Utilities library for ***0xLUN4*** project.
- [aiohttp](https://docs.aiohttp.org/en/stable/): Asynchronous HTTP client/server library.

## Usage

To use the `Stream` and `Game` classes, create instances and call their methods to interact with Twitch stream information.

Example:

```python
from Twitch.stream import Stream, Game

# Create Stream and Game instances
twitch_stream = Stream(config, logger)
twitch_game = Game(config, logger)

# Get stream information
info = await twitch_stream.get_info(user_id)

# Set stream information
await twitch_stream.set_info(user_id, title="New Title", game_name="New Game", language="en", tags=["tag1", "tag2"])

# Get game id
game_id = await twitch_game.get_id("Game Name")
```
