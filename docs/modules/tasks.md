# TaskHandler Documentation

## Overview

`task_handler.py` provides a class to handle tasks. The task queue is used to queue tasks related to both Discord or Twitch. The task queue is based on asyncio.Queue and can be used to add and get tasks concurrently.

### About

This script introduces a `Task` class and a `TaskQueue` class for managing tasks. The `Task` class represents a task, and the `TaskQueue` class manages the task queue.

## Class: `Task`

### Initialization

```python
def __init__(self, action: str, data: dict, instant: bool, timeframe: int, role: str, task_id: int = None, date: int = None):
    """
    Initializes the Task class.

    Args:
        action (str): The action associated with the task.
        data (dict): Data related to the task.
        instant (bool): True if the task should be executed instantly, False if the task should be queued.
        timeframe (int): The time frame for the task.
        role (str): The role associated with the task.
        task_id (int): The task ID. If not provided, it will be automatically generated.
        date (int): The creation date of the task. If not provided, it will be set to the current timestamp.
    """
```

## Class: `TaskQueue`

### Initialization

```python
def __init__(self, config: dict, logger: logging.Logger):
    """
    Initializes the TaskQueue class.

    Args:
        config (dict): The configuration dictionary.
        logger (logging.Logger): The logger.
    """
```

### Global Constants

```python
def __globals__(self) -> list:
    """
    Returns a list of global constants representing task types.
    """
```

### Methods

#### `add_task(self, task: Task, instant: bool = False) -> None`

- Adds a task to the queue.
  - Args:
    - `task` (Task): The task to add to the queue.
    - `instant` (bool): True if the task should be executed instantly, False if the task should be queued.

#### `get_task(self, instance: bool = False) -> Task`

- Gets a task from the queue.
  - Args:
    - `instance` (bool): True if it's a task that should be executed instantly, False if it's a queued task.
  - Returns:
    - Task: The task from the queue.

#### `get_task_by_id(self, task_id: int) -> Task`

- Gets a task from the queue by its ID.
  - Args:
    - `task_id` (int): The task ID.
  - Returns:
    - Task: The task from the queue.

#### `end_task(self, task: Task) -> None`

- Marks a task as done. This should be called after a task has been completed.
  - Args:
    - `task` (Task): The task to mark as done.

#### `remove_task(self, task: Task) -> None`

- Removes a task from the queue.
  - Args:
    - `task` (Task): The task to remove from the queue.

#### `error_task(self, task: Task) -> None`

- Marks a task as an error. This should be called after a task has been completed with an error.
  - Args:
    - `task` (Task): The task to mark as an error.

#### `get_task_count(self) -> int`

- Gets the number of tasks in the queue.
  - Returns:
    - int: The number of tasks in the queue.

#### `get_task_queue(self) -> list`

- Gets the task queue.
  - Returns:
    - list: The task queue.

#### `load_tasks(self) -> None`

- Loads a list of tasks from an XML file to the queue.

#### `save_tasks(self) -> None`

- Saves a list of tasks from the queue to an XML file.

## Dependencies

- [logging](https://docs.python.org/3/library/logging.html): Module for tracking events and errors.
- [os](https://docs.python.org/3/library/os.html): Module for interacting with the operating system.
- [time](https://docs.python.org/3/library/time.html): Module for time-related functions.
- [xml](https://docs.python.org/3/library/xml.etree.elementtree.html): Module for parsing XML files.

## Configuration

*None*

## Usage

To use the task handler, create an instance of the `Task` class and the `TaskQueue` class. Then, add the task to 
the queue and get the task from the queue.

Example:

```python
from Modules.tasks import Task, TaskQueue

# Create a task
task = Task("test", {"test": "test"}, False, 0, "test")

# Create a task queue
task_queue = TaskQueue(config, logger)

# Add the task to the queue
task_queue.add_task(task)

# Get the task from the queue
task = task_queue.get_task()
```
