#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky

--------

About:
    This script provides a class to handle tasks. The task queue is used to queue tasks that are related to both,
    Discord or Twitch. The task queue is based on asyncio.Queue and can be used to add and get tasks concurrently.

"""

import logging


class Task:
    """
    A class to handle tasks. The task can be any object.
    """
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
        self.tasks = []
        self.finished_tasks = []
        
        self.TASK_TW_TIMEOUT = "twitch_timeout"
        self.TASK_TW_ADD_MODERATOR = "twitch_moderator"
        self.TASK_TW_ADD_VIP = "twitch_vip"
        self.TASK_DC_ADD_ROLE = "discord_role"
        self.TASK_SPECIAL = "special"

    def add_task(self, task: Task) -> None:
        """
        Adds a task to the queue. The task can be any object.
        
        Args:
            task: The task to add to the queue.
        """
        self.tasks.append(task)
        self.logger.info(f'Adding task to queue | {task.action} ({task.id}) | Queue size: {self.get_task_count()}')

    def get_task(self) -> Task:
        """
        Gets a task from the queue. The task can be any object.
        
        Returns:
            Task: The task from the queue.
        """
        task = self.tasks.pop(0)
        self.logger.info(f'Getting task from queue | {task.action} ({task.id}) | Queue size: {self.get_task_count()}')
        return task

    def end_task(self, task: Task) -> None:
        """
        Marks a task as done. This should be called after a task has been completed.
        
        Args:
            task: The task to mark as done.
        """
        self.finished_tasks.append(task)
        self.logger.info(f'Finished task from queue | {task.action} ({task.id}) | Queue size: {self.get_task_count()}')
    
    def get_task_count(self) -> int:
        """
        Gets the number of tasks in the queue.
        
        Returns:
            int: The number of tasks in the queue.
        """
        return len(self.tasks)
    
    def get_task_queue(self) -> list:
        """
        Gets the task queue.
        
        Returns:
            list: The task queue.
        """
        return self.tasks
