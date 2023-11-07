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
import json
import logging
import os


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
        self.load_tasks()
        
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
    
    def load_tasks(self) -> None:
        """
        Loads a list of tasks from a json file to the queue.
        """
        if os.path.exists(f'Modules/data/tasks.json'):
            with open(f'Modules/data/tasks.json', 'r') as f:
                task_data = json.load(f)
                tasks = task_data['tasks']
                finished = task_data['finished']
            for task in tasks:
                self.tasks.append(Task(task['action'], task['data']))
            for task in finished:
                self.finished_tasks.append(Task(task['action'], task['data']))
            self.logger.info(f'Loaded Tasks | Queue size: {self.get_task_count()} | Finished: {len(self.finished_tasks)}')
        
        else:
            if not os.path.exists(f'Modules/data/'):
                os.makedirs(f'Modules/data/')
            with open(f'Modules/data/tasks.json', 'w') as f:
                json.dump({"tasks": [], "finished": []}, f, indent=4)
            self.logger.info(f'Initialized Tasks | Queue size: {self.get_task_count()} | Finished: {len(self.finished_tasks)}')
        
        Task._task_id_counter = self.tasks[-1].id if len(self.tasks) > 0 else 0
    
    def save_tasks(self) -> None:
        """
        Saves a list of tasks from the queue to a json file.
        """
        tasks = []
        finished = []
        
        for task in self.tasks:
            tasks.append({
                "id": task.id,
                "action": task.action,
                "data": task.data
            })
        
        for task in self.finished_tasks:
            finished.append({
                "id": task.id,
                "action": task.action,
                "data": task.data
            })
            
        task_data = {
            "tasks": tasks,
            "finished": finished
        }
        with open(f'Modules/data/tasks.json', 'w') as f:
            json.dump(task_data, f, indent=4)
        self.logger.info(f'Saved Tasks | Queue size: {self.get_task_count()} | Finished: {len(self.finished_tasks)}')
