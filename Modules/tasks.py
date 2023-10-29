import asyncio
import logging


class Task:
    _task_id_counter = 0

    def __init__(self, action, data):
        Task._task_id_counter += 1
        self.id = Task._task_id_counter
        self.action = action
        self.data = data


class TaskQueue:
    """
    A queue that can be used to add and get tasks. The queue is based on asyncio.Queue and can be used to add and get
    tasks concurrently. The queue can be used to add and get any object as a task, but it is recommended to use a
    dictionary.
    
    Args:
        config (dict): The configuration dictionary.
        logger (logging.Logger): The logger.
    """
    def __init__(self, config: dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.tasks = asyncio.Queue()

    async def add_task(self, task) -> None:
        """
        Adds a task to the queue. The task can be any object.
        
        Args:
            task: The task to add to the queue.
        """
        await self.tasks.put(task)
        self.logger.info(f'Adding task to queue | {task.action} ({task.id})')

    async def get_task(self) -> any:
        """
        Gets a task from the queue. The task can be any object.
        
        Returns:
            any: The task from the queue.
        """
        task = await self.tasks.get()
        
        self.logger.info(f'Getting task from queue | {task.action} ({task.id})')
        return task

    def task_done(self):
        """
        Marks a task as done. This should be called after a task has been completed.
        """
        self.tasks.task_done()
        self.logger.info(f'Finished task from queue')