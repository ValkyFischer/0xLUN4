# Twitch.channel Documentation

## Overview

`Twitch/channel.py` provides functionality to interact with Twitch channels. It includes a `Channel` class with methods to set up a channel, get information about emotes, followers, subscribers, VIPs, moderators, bans, and stream details.

### About

This script introduces a `Channel` class, allowing you to manage various aspects of a Twitch channel.

## Class: `Channel`

### Initialization

```python
def __init__(self, config: dict, logger: ValkyrieLogger, stream: Stream):
    """
    Initializes the Channel class.

    Args:
        config (dict): The configuration dictionary.
        logger (ValkyrieLogger): The logger.
        stream (Stream): The Stream instance for stream-related operations.
    """
```

### Methods

#### `setup(self) -> None`

- Sets up the channel by obtaining information about emotes, followers, subscribers, VIPs, moderators, bans, and stream details.

### Methods - Getter

#### `get_id(self, username: str) -> int`

- Gets the user id of a channel.

    - Args:
        - `username` (str): The username of the channel.

    - Returns:
        - int: The user id of the channel.

#### `get_status(self) -> bool`

- Gets the live status of a channel.

    - Returns:
        - bool: `True` if the channel is live, `False` otherwise.

#### `get_emotes(self) -> list`

- Gets the emotes of a channel.

    - Returns:
        - list: List of emotes in the channel.

#### `get_followers(self, total: bool = False) -> list`

- Gets the followers of a channel.

    - Args:
        - `total` (bool): If `True`, returns the total count of followers instead of a list.

    - Returns:
        - list or int: List of followers or total count depending on the `total` parameter.

#### `get_subscribers(self, total: bool = False) -> list`

- Gets the subscribers of a channel.

    - Args:
        - `total` (bool): If `True`, returns the total count of subscribers instead of a list.

    - Returns:
        - list or int: List of subscribers or total count depending on the `total` parameter.

#### `get_moderators(self) -> list`

- Gets the moderators of a channel.

    - Returns:
        - list: List of moderators in the channel.

#### `get_vips(self) -> list`

- Gets the VIPs of a channel.

    - Returns:
        - list: List of VIPs in the channel.

#### `get_bans(self) -> list`

- Gets the bans of a channel.

    - Returns:
        - list: List of banned users in the channel.

### Methods - Setter
#### `mod(self, mod_id: int | str) -> None`

- Adds a moderator to a channel.

    - Args:
        - `mod_id` (int or str): The user id or username of the user to be modded.

#### `unmod(self, mod_id: int | str) -> None`

- Removes a moderator from a channel.

    - Args:
        - `mod_id` (int or str): The user id or username of the user to be unmodded.

#### `vip(self, vip_id: int | str) -> None`

- Adds a VIP to a channel.

    - Args:
        - `vip_id` (int or str): The user id or username of the user to be added as VIP.

#### `unvip(self, vip_id: int | str) -> None`

- Removes a VIP from a channel.

    - Args:
        - `vip_id` (int or str): The user id or username of the user to be removed from VIP.

#### `timeout(self, timeout_id: int | str, duration: int = 600, reason: str = "VALKBOT_NO_REASON") -> None`

- Times out a user in a channel.

    - Args:
        - `timeout_id` (int or str): The user id or username of the user to be timed out.
        - `duration` (int): The duration of the timeout in seconds.
        - `reason` (str): The reason for the timeout.

#### `untimeout(self, timeout_id: int | str) -> None`

- Removes a timeout from a channel.

    - Args:
        - `timeout_id` (int or str): The user id or username of the user to be untimed out.

#### `ban(self, ban_id: int | str, reason: str = "VALKBOT_NO_REASON") -> None`

- Adds a ban to a channel.

    - Args:
        - `ban_id` (int or str): The user id or username of the user to be banned.
        - `reason` (str): The reason for the ban.

#### `unban(self, ban_id: int | str) -> None`

- Removes a ban or a timeout from a channel.

    - Args:
        - `ban_id` (int or str): The user id or username of the user to be unbanned.

#### `announce(self, message: str, color: str = "primary") -> None`

- Sends an announcement in a channel.

    - Args:
        - `message` (str): The announcement message.
        - `color` (str): The color of the announcement message (default is "primary").

#### `whisper(self, to_user_id: int | str, message: str) -> None`

- Sends a whisper message to the specified user.

    - Args:
        - `to_user_id` (int or str): The user id or username of the user to receive the whisper.
        - `message` (str): The whisper message.

### Methods - Checker
#### `is_live(self) -> bool`

- Checks if a channel is live.

    - Returns:
        - bool: `True` if the channel is live, `False` otherwise.

#### `is_follower(self, username: str) -> bool`

- Checks if a user is a follower of a channel.

    - Args:
        - `username` (str): The username of the user.

    - Returns:
        - bool: `True` if the user is a follower, `False` otherwise.

#### `is_sub(self, username: str) -> bool`

- Checks if a user is a subscriber of a channel.

    - Args:
        - `username` (str): The username of the user.

    - Returns:
        - bool: `True` if the user is a subscriber, `False` otherwise.

#### `is_vip(self, username: str) -> bool`

- Checks if a user is a VIP of a channel.

    - Args:
        - `username` (str): The username of the user.

    - Returns:
        - bool: `True` if the user is a VIP, `False` otherwise.

#### `is_mod(self, username: str) -> bool`

- Checks if a user is a moderator of a channel.

    - Args:
        - `username` (str): The username of the user.

    - Returns:
        - bool: `True` if the user is a moderator, `False

` otherwise.

#### `is_banned(self, username: str) -> bool`

- Checks if a user is banned from a channel.

    - Args:
        - `username` (str): The username of the user.

    - Returns:
        - bool: `True` if the user is banned, `False` otherwise.

## Dependencies

- [logging](https://docs.python.org/3/library/logging.html): Module for tracking events and errors.
- [aiohttp](https://docs.aiohttp.org/en/stable/): Asynchronous HTTP client/server library.

## Configuration

The `Channel` class relies on configuration settings provided in the overall project configuration dictionary.

## Usage

To use the `Channel` class, create an instance, and then call the `setup` method to initialize and fetch channel information.

Example:

```python
from Twitch.channel import Channel

# Create a Channel instance
twitch_channel = Channel(config, logger, stream_instance)

# Set up the channel
await twitch_channel.setup()
```
