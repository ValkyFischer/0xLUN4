#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky

--------

About:
    This script is the main bot script that will run the Valkyrie Bot. This bot is used to connect the functionality of
    both, the Discord bot and the Twitch bot. This bot will also handle and work through the task queue. The task queue
    is used to queue tasks that are related to both, Discord or Twitch.

"""
import asyncio
import datetime
import os
import time

from ValkyrieUtils.Logger import ValkyrieLogger

from bot_discord import DiscordBot
from bot_twitch import TwitchBot

from Modules.tasks import TaskQueue, Task


class ValkyrieBot:
    """
    A class which operates tasks that are related to both, Discord or Twitch. This class is used to connect
    the functionality of both bots.
    
    Args:
        twitch_bot (TwitchBot): The Twitch bot instance.
        discord_bot (DiscordBot): The Discord bot instance.
        config (dict): The configuration file.
        logger (ValkyrieLogger): The logger instance.
        task_queue (TaskQueue): The queue instance.
    """
    def __init__(self, twitch_bot: TwitchBot, discord_bot: DiscordBot, config: dict, logger: ValkyrieLogger, task_queue: TaskQueue):
        self.ready = False
        self.empty = False
        self.init = False
        self.running = None
        self.twitch_bot = twitch_bot
        self.discord_bot = discord_bot
        self.config = config
        self.logger = logger
        self.task_queue = task_queue
        
        self.refresh_time = datetime.datetime.now()
        self.refresh_interval = 10800
        
        self.backup_task = 0
        self.backup_finished = 0
        self.backup_deleted = 0
        self.backup_errors = 0
    
    async def check_refresh(self):
        """
        A method which checks if the Twitch API token needs to be refreshed. The Twitch API token will be refreshed
        every N seconds. The N seconds interval is defined in the configuration file.
        """
        # ready check
        if not self.ready:
            return
        
        # continue
        if (datetime.datetime.now() - self.refresh_time).total_seconds() > self.refresh_interval:
            self.logger.info(f'Refreshing Twitch API token')
            self.twitch_bot.user_token = self.twitch_bot.auth.authorize(
                self.config['twitch']['user']['client_id'],
                self.config['twitch']['user']['client_secret'],
                self.config['twitch']['redirect_uri'],
                self.twitch_bot.scopes,
                "user"
            )
            await self.discord_bot.send_log(f"Refreshed User Twitch API token")
            self.twitch_bot.bot_token = self.twitch_bot.auth.authorize(
                self.config['twitch']['bot']['client_id'],
                self.config['twitch']['bot']['client_secret'],
                self.config['twitch']['redirect_uri'],
                self.twitch_bot.scopes,
                "bot"
            )
            await self.discord_bot.send_log(f"Refreshed Bot Twitch API token")
            self.refresh_time = datetime.datetime.now()
    
    async def check_live(self):
        """
        A method which checks if a channel is live or not. If a channel goes live or offline, a
        notification will be sent to the Discord server.
        """
        # ready check
        if not self.ready:
            return
        
        # continue
        channel = self.twitch_bot.channel.name
        is_live = await self.twitch_bot.channel.get_status()
        old_status = self.twitch_bot.channel.is_live
        if not self.init:
            self.init = True
            self.twitch_bot.channel.is_live = is_live
            self.logger.info(f'Twitch Live Loop | {channel} live check | {is_live}')
        
        if old_status != is_live:
            if is_live:
                await self.discord_bot.send_notification(f'{channel}')
                self.logger.info(f'Channel went live | {channel}')
            else:
                await self.discord_bot.send_log(f'{channel} went offline')
                self.logger.info(f'Channel went offline | {channel}')
            self.twitch_bot.channel.is_live = is_live
    
    async def check_unmod(self):
        """
        A method which checks if a moderator is still a moderator based on the Twitch/data/rewards/moderators.txt file.
        The duration of the moderator role is defined in the configuration file in seconds. If a moderator is no longer
        a moderator, the role will be removed.
        """
        # ready check
        if not self.ready:
            return
        
        # continue
        for rwd in self.config['twitch']['rewards']:
            if rwd['task'].lower() == self.task_queue.TASK_TW_ADD_MODERATOR:
                duration = rwd['time']
                if os.path.exists('Twitch/data/rewards/moderators.txt'):
                    with open('Twitch/data/rewards/moderators.txt', 'r') as f:
                        lines = f.readlines()
                        for line in lines:
                            line = line.strip()
                            time_count, user_name = line.split('|')
                            time_dtime = datetime.datetime.strptime(time_count, '%Y-%m-%d %H:%M:%S')
                            if (datetime.datetime.now() - time_dtime).total_seconds() > duration:
                                await self.twitch_bot.channel.unmod(user_name)
                                self.logger.info(f'Removing moderator role | {user_name}')
                                lines.remove(line)
                break
    
    async def check_queue(self, instant: bool = False):
        """
        A method which checks the queue for tasks. If a task is found, it will be executed.
        
        Args:
            instant: True if the task should be executed instantly, False if not.
        
        Actions:
            - TASK_DC_ADD_ROLE: Adds a role to a Discord user.
            - TASK_TW_ADD_MODERATOR: Adds a moderator role to a Twitch user.
            - TASK_TW_ADD_VIP: Adds a VIP role to a Twitch user.
            - TASK_TW_TIMEOUT: Times out a Twitch user.
            - TASK_SPECIAL: Sends a special message to a Discord channel.
        """
        # ready check
        if not self.ready:
            return
        
        # continue - instant
        if instant:
            if len(self.task_queue.instant_tasks) > 0:
                task = self.task_queue.get_task(True)
                self.logger.info(f'Executing instant task | {task.action} | {task.data}')
                if await self.execute_task(task):
                    self.task_queue.end_task(task)
                else:
                    self.task_queue.error_task(task)
        
        # continue - normal
        else:
            if self.task_queue.get_task_count() == 0:
                if not self.empty:
                    self.empty = True
                    self.logger.info(f'Observing task queue is empty')
            else:
                self.empty = False
                q = self.task_queue.get_task_count()
                for i in range(q):
                    
                    task = self.task_queue.get_task()
                    self.logger.info(f'Executing task from queue | {i + 1}/{q} | {task.action} | {task.data}')
                    if await self.execute_task(task):
                        self.task_queue.end_task(task)
                    else:
                        self.task_queue.error_task(task)
    
    async def backup_tasks(self):
        """
        A method which backs up the task queue to a file.
        """
        # ready check
        if not self.ready:
            return
        
        # continue
        q_size = self.task_queue.get_task_count()
        f_size = len(self.task_queue.finished_tasks)
        d_size = len(self.task_queue.deleted_tasks)
        e_size = len(self.task_queue.errors)
        
        if (self.backup_task != q_size or self.backup_finished != f_size
                or self.backup_deleted != d_size or self.backup_errors != e_size):
            self.logger.info(f'BackUp Tasks | Old: {self.backup_task}/{self.backup_finished}/{self.backup_deleted}/{self.backup_errors} | New: {q_size}/{f_size}/{d_size}/{e_size}')
            
            self.backup_task = q_size
            self.backup_finished = f_size
            self.backup_deleted = d_size
            self.backup_errors = e_size
            
            self.task_queue.save_tasks()
    
    async def execute_task(self, task: Task):
        err = True
        if task.action == self.task_queue.TASK_DC_ADD_ROLE:
            await self.discord_bot.assign_role(
                task.data['user_input'] if 'user_input' in task.data else task.data['user_name'])
            await self.discord_bot.send_log(
                f"Assigned Discord Role | {task.data['user_input'] if 'user_input' in task.data else task.data['user_name']}")
            self.logger.info(f'Assigning role | {task.data["user_name"]}')
            err = False
        
        elif task.action == self.task_queue.TASK_TW_ADD_MODERATOR:
            await self.twitch_bot.channel.mod(task.data['user_name'])
            await self.discord_bot.send_log(
                f"Added Twitch Moderator | {task.data['user_input'] if 'user_input' in task.data else task.data['user_name']}")
            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('Twitch/data/rewards/moderators.txt', 'a+') as f:
                f.write(f'{time_now}|{task.data["user_name"]}\n')
            err = False
        
        elif task.action == self.task_queue.TASK_TW_ADD_VIP:
            await self.twitch_bot.channel.vip(task.data['user_name'])
            await self.discord_bot.send_log(
                f"Added Twitch VIP | {task.data['user_input'] if 'user_input' in task.data else task.data['user_name']}")
            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('Twitch/data/rewards/vips.txt', 'a+') as f:
                f.write(f'{time_now}|{task.data["user_name"]}\n')
            err = False
        
        elif task.action == self.task_queue.TASK_TW_TIMEOUT:
            for rwd in self.config['twitch']['rewards']:
                if rwd['name'].lower() == task.data['reward_name'].lower():
                    duration = rwd['time']
                    await self.twitch_bot.channel.timeout(
                        timeout_id = task.data['user_input'] if 'user_input' in task.data else task.data['user_name'],
                        duration = duration,
                        reason = f'ValkyrieBot | {task.data["user_name"]} has timed you out for {task.data["reward_cost"]} Divine Potions!'
                    )
                    await self.discord_bot.send_log(
                        f"Timed out Twitch User | {task.data['user_input'] if 'user_input' in task.data else task.data['user_name']} | {duration} seconds")
                    err = False
                    break
            else:
                self.logger.warning(f'Unknown Reward Redemption | {task.data["reward_name"]}')
                await self.discord_bot.send_log(f"Unknown Reward Redemption | {task.data['reward_name']}")
        
        elif task.action == self.task_queue.TASK_SPECIAL:
            # await self.discord_bot.send_special(task.data)
            self.logger.warning(f'Not implemented: {task.action}')
            await self.discord_bot.send_log(f"Not implemented: {task.action}")
        
        else:
            self.logger.warning(f'Unknown task action: {task.action}')
            await self.discord_bot.send_log(f"Unknown task action: {task.action}")
        
        if err:
            return False
        else:
            return True
    
    async def ready_up(self):
        self.running = True
        if not self.ready:
            if self.discord_bot.loaded and self.twitch_bot.loaded:
                self.ready = True
                self.logger.info(f'=' * 103)
                self.logger.info(f'ValkyrieBot fully loaded')
                self.logger.info(f'=' * 103)
    
    async def run(self):
        """
        A loop which runs the main bot methods every N seconds. The N seconds interval is defined in the configuration
        file.
        """
        while True:
            start_time = time.time()
            interval_seconds = self.config['interval'] if self.ready else 1
            
            await self.ready_up()
            
            await self.check_unmod()
            await self.check_queue()
            await self.check_refresh()
            await self.check_live()
            
            await self.backup_tasks()
            
            sleep_duration = interval_seconds - (time.time() - start_time)
            await asyncio.sleep(sleep_duration)
    
    async def run_fast(self):
        """
        A loop which runs the main bot methods every N seconds. The N seconds interval is defined in the configuration
        file.
        """
        while True:
            start_time = time.time()
            interval_seconds = 1
            if self.ready:
                await self.check_queue(True)
            
            sleep_duration = interval_seconds - (time.time() - start_time)
            await asyncio.sleep(sleep_duration)
    
    async def stop(self):
        """
        A method which stops the bot.
        """
        self.running = False
        self.logger.info(f'ValkyrieBot stopped')
