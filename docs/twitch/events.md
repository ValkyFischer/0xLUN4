# Twitch.events Documentation

## Overview

`Twitch/events.py` provides functionality for the Twitch bot to handle events. This script defines an `Event` class with various methods representing different events that the bot can respond to.

### About

This script handles various events that the Twitch bot might encounter, such as users cheering bits, redeeming channel points, or subscribing to the channel.

## Class: `Event`

### Initialization

```python
def __init__(self, bot):
    """
    Initializes the Event class.

    Args:
        bot: The Twitch bot instance.
    """
```

### Methods

#### `on_ready(self) -> None`

- This event is called once when the bot goes online. It is used to set up the bot and subscribe to topics.

  - Args:
    - None

#### `on_bits(self, event: pubsub.PubSubBitsMessage) -> None`

- This event is called when a user cheers bits.

  - Args:
    - `event` (pubsub.PubSubBitsMessage): The event.

#### `on_channel_points(self, event: pubsub.PubSubChannelPointsMessage) -> None`

- This event is called when a user redeems a channel point reward. It creates and puts a new task into the task queue.

  - Args:
    - `event` (pubsub.PubSubChannelPointsMessage): The event.

#### `on_subscriptions(self, event: pubsub.PubSubChannelSubscribe) -> None`

- This event is called when a user subscribes to the channel.

  - Args:
    - `event` (pubsub.PubSubChannelSubscribe): The event.

## Dependencies

- [random](https://docs.python.org/3/library/random.html): Standard Python random module.
- [twitchio](https://twitchio.dev/en/stable/): TwitchIO extension for handling PubSub events.
- [tasks](../modules/tasks.md): Custom module for managing tasks.

## Usage

To use the `Event` class, create an instance, and TwitchIO will automatically call the appropriate event methods when events occur.

Example:

```python
from Twitch.events import Event

# Create an Event instance
twitch_events = Event(bot_instance)

# TwitchIO will automatically call event methods when corresponding events occur
```