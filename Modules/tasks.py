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
import time
import xml.etree.ElementTree as ET


class Task:
    """
    A class to handle tasks. The task can be any object.
    """
    _task_id_counter = 0

    def __init__(self, action: str, data: dict, instant: bool, timeframe: int, role: str, task_id: int = None, date: int = None):
        Task._task_id_counter += 1
        self.id = Task._task_id_counter if task_id is None else task_id
        self.action = action
        self.data = data
        self.instant = instant
        self.time = timeframe
        self.role = role
        self.date = time.time() if date is None else date


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
        self.instant_tasks = []
        self.finished_tasks = []
        self.deleted_tasks = []
        self.errors = []
        self.path_tasks = 'Modules/data/tasks.xml'
        
        self.TASK_TW_TIMEOUT = "twitch_timeout"
        self.TASK_TW_BAN = "twitch_ban"
        self.TASK_TW_UNBAN = "twitch_unban"
        self.TASK_TW_ADD_MODERATOR = "twitch_moderator"
        self.TASK_TW_REM_MODERATOR = "twitch_moderator_rem"
        self.TASK_TW_ADD_VIP = "twitch_vip"
        self.TASK_TW_REM_VIP = "twitch_vip_rem"
        self.TASK_DC_ADD_ROLE = "discord_role"
        self.TASK_DC_REM_ROLE = "discord_role_rem"
        self.TASK_SPECIAL = "special"

        self.load_tasks()
    
    def __globals__(self):
        """
        This method is called to receive globals.
        """
        TASKS = [
            self.TASK_TW_TIMEOUT,
            self.TASK_TW_BAN,
            self.TASK_TW_UNBAN,
            
            self.TASK_TW_ADD_MODERATOR,
            self.TASK_TW_REM_MODERATOR,
            
            self.TASK_TW_ADD_VIP,
            self.TASK_TW_REM_VIP,
            
            self.TASK_DC_ADD_ROLE,
            
            self.TASK_SPECIAL,
        ]
        return TASKS

    def add_task(self, task: Task, instant: bool = False) -> None:
        """
        Adds a task to the queue. The task can be any object.
        
        Args:
            task: The task to add to the queue.
            instant: True if the task should be executed instantly, False if the task should be queued.
        """
        if task.instant or instant:
            self.instant_tasks.append(task)
            self.logger.info(f'Adding Instant Task | {task.action} ({task.id})')
        else:
            self.tasks.append(task)
            self.logger.info(f'Adding Task | {task.action} ({task.id}) | Queue size: {self.get_task_count()}')

    def get_task(self, instance: bool = False) -> Task:
        """
        Gets a task from the queue. The task can be any object.
        
        Args:
            instance: True if it's a task which should be executed instantly, False if it's a queued task.
        
        Returns:
            Task: The task from the queue.
        """
        task = self.tasks.pop(0) if not instance else self.instant_tasks.pop(0)
        self.logger.info(f'Getting Task | {task.action} ({task.id}) | Queue size: {self.get_task_count()}')
        return task
    
    def get_task_by_id(self, task_id: int) -> Task:
        """
        Gets a task from the queue by its id. The task can be any object.
        
        Args:
            task_id: The task id.
        
        Returns:
            Task: The task from the queue.
        """
        for task in self.tasks:
            if task.id == task_id:
                return self.tasks.pop(self.tasks.index(task))
        for task in self.finished_tasks:
            if task.id == task_id:
                return self.finished_tasks.pop(self.finished_tasks.index(task))
        for task in self.deleted_tasks:
            if task.id == task_id:
                return self.deleted_tasks.pop(self.deleted_tasks.index(task))
        for task in self.errors:
            if task.id == task_id:
                return self.errors.pop(self.errors.index(task))

    def end_task(self, task: Task) -> None:
        """
        Marks a task as done. This should be called after a task has been completed.
        
        Args:
            task: The task to mark as done.
        """
        self.finished_tasks.append(task)
        self.logger.info(f'Finished Task | {task.action} ({task.id}) | Queue size: {self.get_task_count()}')
    
    def remove_task(self, task: Task) -> None:
        """
        Removes a task from the queue.
        
        Args:
            task: The task to remove from the queue.
        """
        self.deleted_tasks.append(task)
        self.logger.info(f'Removed Task | {task.action} ({task.id})')
    
    def error_task(self, task: Task) -> None:
        """
        Marks a task as an error. This should be called after a task has been completed with an error.
        
        Args:
            task: The task to mark as an error.
        """
        self.errors.append(task)
        self.logger.warning(f'Error Task | {task.action} ({task.id}) | Queue size: {self.get_task_count()}')
    
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
        Loads a list of tasks from an XML file to the queue.
        """
        
        def parse_task_element(tel: ET.Element) -> Task:
            """
            Parses a task element from an XML file.
            
            Args:
                tel: The task element.
            """
            task_id = int(tel.get("id"))
            task_action = tel.get("action")
            task_instant = tel.get("instant") == "True"
            task_data = {k: tel.get(k) for k in tel.keys() if k not in ["id", "action", "instant"]}
            time_frame = tel.get("time") if "time" in tel.keys() else None
            role_assign = tel.get("role") if "role" in tel.keys() else None
            creation_date = tel.get("date") if "date" in tel.keys() else None
            return Task(task_action, task_data, task_instant, time_frame, role_assign, task_id, creation_date)
        
        # If the XML file exists, load the tasks from the file
        if os.path.exists(self.path_tasks):
            tree = ET.parse(self.path_tasks)
            root = tree.getroot()
            
            t_template = {"tasks": [], "finished": [], "deleted": [], "errors": []}
            
            for element in root:
                key = element.tag
                for task_element in element:
                    task = parse_task_element(task_element)
                    t_template[key].append(task)
            
            self.tasks = t_template["tasks"]
            self.finished_tasks = t_template["finished"]
            self.deleted_tasks = t_template["deleted"]
            self.errors = t_template["errors"]
            
            self.logger.info(f'Loaded Tasks | Queue size: {self.get_task_count()} | Finished: {len(self.finished_tasks)} | Deleted: {len(self.deleted_tasks)} | Errors: {len(self.errors)}')
        
        # If the XML file does not exist, create it
        else:
            if not os.path.exists('Modules/data/'):
                os.makedirs('Modules/data/')
            self.save_tasks()
            self.logger.info(f'Initialized Tasks | Queue size: {self.get_task_count()} | Finished: {len(self.finished_tasks)} | Deleted: {len(self.deleted_tasks)} | Errors: {len(self.errors)}')
        
        Task._task_id_counter = sum([len(self.tasks), len(self.finished_tasks), len(self.deleted_tasks), len(self.errors)])
    
    def save_tasks(self) -> None:
        """
        Saves a list of tasks from the queue to an XML file.
        """
        
        def indent(elem, level = 0):
            """Indented formatting for XML"""
            i = "\n" + level * "    "
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "    "
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for elem in elem:
                    indent(elem, level + 1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i
        
        task_data = {
            "tasks": self.tasks,
            "finished": self.finished_tasks,
            "deleted": self.deleted_tasks,
            "errors": self.errors
        }
        
        root = ET.Element("TaskData")
        for key, value in task_data.items():
            sub_element = ET.SubElement(root, key)
            for task in value:
                task_element = ET.SubElement(sub_element, "Task")
                task_element.set("id", str(task.id))
                task_element.set("action", task.action)
                task_element.set("instant", str(task.instant))
                task_element.set("date", str(task.date))
                if task.time is not None:
                    task_element.set("time", str(task.time))
                if task.role is not None:
                    task_element.set("role", str(task.role))
                for data_key, data_value in task.data.items():
                    task_element.set(data_key, str(data_value))
        
        tree = ET.ElementTree(root)
        indent(root)
        tree.write(self.path_tasks, encoding = 'utf-8', xml_declaration = True)
    
