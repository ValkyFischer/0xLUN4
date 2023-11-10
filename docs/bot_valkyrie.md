# ValkyrieBot Documentation

## Overview

`bot_valkyrie.py` is the main bot script that runs the Valkyrie Bot. This bot integrates the functionalities of both the Discord bot and the Twitch bot. It also handles and processes tasks through a task queue, which can be related to either Discord or Twitch.

### About

This script initializes the Valkyrie Bot, connects the Discord and Twitch bots, and manages a task queue for processing various tasks.

## Class: `ValkyrieBot`

```python
def __init__(self, twitch_bot: TwitchBot, discord_bot: DiscordBot, config: dict, logger: ValkyrieLogger, task_queue: TaskQueue):
    """
    Initializes the ValkyrieBot class.

    Args:
        twitch_bot (TwitchBot): The Twitch bot instance.
        discord_bot (DiscordBot): The Discord bot instance.
        config (dict): The configuration dictionary.
        logger (ValkyrieLogger): The logger instance.
        task_queue (TaskQueue): The queue instance.
    """
```

### Attributes

- `ready`: Indicates whether the bot is fully loaded and ready to operate.
- `empty`: Indicates whether the task queue is empty.
- `init`: Indicates whether the bot has been initialized.
- `running`: Indicates whether the bot is currently running.
- `twitch_bot`: Instance of the TwitchBot class.
- `discord_bot`: Instance of the DiscordBot class.
- `config`: The configuration dictionary.
- `logger`: The logger instance.
- `task_queue`: The TaskQueue instance.
- `refresh_time`: Timestamp for tracking the last Twitch API token refresh.
- `refresh_interval`: Interval for refreshing the Twitch API token, defined in the configuration file.
- `backup_task`, `backup_finished`, `backup_deleted`, `backup_errors`: Backup counters for tracking task queue changes.
- `start_time`: Timestamp indicating the bot's start time.

### Methods

#### `check_refresh(self)`
- Checks if the Twitch API token needs to be refreshed and performs the refresh.

#### `check_live(self)`
- Checks if a Twitch channel is live or offline and sends notifications accordingly.

#### `check_unmod(self)`
- Checks if a moderator is still a moderator based on the `Twitch/data/rewards/moderators.txt` file and removes the role if necessary.

#### `check_queue(self, instant: bool = False)`
- Checks the task queue for tasks and executes them.
- Args:
  - `instant` (bool): True if the task should be executed instantly, False if not.

#### `backup_tasks(self)`
- Backs up the task queue to a file.

#### `execute_task(self, task: Task) -> bool`
- Executes a given task.
- Args:
  - `task` (Task): The task to execute.
- Returns:
  - bool: True if the task was executed successfully, False if not.

#### `ready_up(self)`
- Checks if both the Discord and Twitch bots are loaded and marks the ValkyrieBot as ready.

#### `run(self)`
- Runs the main bot loop, executing key methods at regular intervals defined in the configuration file.

#### `run_fast(self)`
- Runs a loop checking the task queue more frequently (every 1 second) for instant tasks.

#### `stop(self)`
- Stops the bot.

## Dependencies

- [ValkyrieUtils](https://github.com/ValkyFischer/ValkyrieUtils): Utilities library for the ***0xLUN4*** project.
- [tasks](modules/tasks.md): Custom module for managing tasks.
- [asyncio](https://docs.python.org/3/library/asyncio.html): Standard Python asyncio module.
- [datetime](https://docs.python.org/3/library/datetime.html): Standard Python datetime module.
- [os](https://docs.python.org/3/library/os.html): Module for interacting with the operating system.
- [time](https://docs.python.org/3/library/time.html): Module for time-related functions.

## Usage

To use the `ValkyrieBot` class, create an instance and call its `run` method.

Example:

```python
from bot_valkyrie import ValkyrieBot
from bot_discord import DiscordBot
from bot_twitch import TwitchBot

# Create instances of DiscordBot and TwitchBot
discord_bot = DiscordBot(config, logger, task_queue)
twitch_bot = TwitchBot(config, logger, task_queue)

# Create ValkyrieBot instance
valkyrie_bot = ValkyrieBot(twitch_bot, discord_bot, config, logger, task_queue)

# Run the ValkyrieBot
await valkyrie_bot.run()
```

```python
# To stop the ValkyrieBot
await valkyrie_bot.stop()
```