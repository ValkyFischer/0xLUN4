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

from ValkyrieUtils.Logger import ValkyrieLogger

from bot_discord import DiscordBot
from bot_twitch import TwitchBot

from Modules.tasks import TaskQueue


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
        self.twitch_bot = twitch_bot
        self.discord_bot = discord_bot
        self.config = config
        self.logger = logger
        self.task_queue = task_queue
    
    async def check_live(self):
        """
        A method which checks if a channel is live or not. If a channel goes live or offline, a
        notification will be sent to the Discord server.
        """
        if self.discord_bot.loaded and self.twitch_bot.loaded:
            channel = self.twitch_bot.channel.name
            is_live = await self.twitch_bot.channel.get_status()
            old_status = self.twitch_bot.channel.is_live
            if not self.ready:
                self.ready = True
                self.twitch_bot.channel.is_live = is_live
                self.logger.info(f'INIT Loop | {channel} live check | {is_live}')
                self.logger.info(f'=' * 103)
                self.logger.info(f'ValkyrieBot fully loaded')
                self.logger.info(f'=' * 103)
            
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
        for rwd in self.config['twitch']['rewards']:
            if rwd['task'].lower() == self.task_queue.TASK_TW_ADD_MODERATOR:
                duration = rwd['time']
                if os.path.exists('Twitch/data/rewards/moderators.txt'):
                    with open('Twitch/data/rewards/moderators.txt', 'r') as f:
                        lines = f.readlines()
                        for line in lines:
                            line = line.strip()
                            time, user_name = line.split('|')
                            time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                            if (datetime.datetime.now() - time).total_seconds() > duration:
                                await self.twitch_bot.channel.unmod(user_name)
                                self.logger.info(f'Removing moderator role | {user_name}')
                                lines.remove(line)
                break
    
    async def check_queue(self):
        """
        A method which checks the queue for tasks. If a task is found, it will be executed.
        
        Actions:
            - TASK_DC_ADD_ROLE: Adds a role to a Discord user.
            - TASK_TW_ADD_MODERATOR: Adds a moderator role to a Twitch user.
            - TASK_TW_ADD_VIP: Adds a VIP role to a Twitch user.
            - TASK_TW_TIMEOUT: Times out a Twitch user.
            - TASK_SPECIAL: Sends a special message to a Discord channel.
        """
        if self.task_queue.tasks.empty():
            if not self.empty:
                self.empty = True
                self.logger.info(f'Observing task queue is empty')
        else:
            self.empty = False
            q = self.task_queue.tasks.qsize()
            for i in range(q):
                task = await self.task_queue.get_task()
                
                if task.action == self.task_queue.TASK_DC_ADD_ROLE:
                    await self.discord_bot.assign_role(task.data['user_input'] if 'user_input' in task.data else task.data['user_name'])
                    await self.discord_bot.send_log(f"Assigned Discord Role | {task.data['user_input'] if 'user_input' in task.data else task.data['user_name']}")
                    self.logger.info(f'Assigning role | {task.data["user_name"]}')
                    
                elif task.action == self.task_queue.TASK_TW_ADD_MODERATOR:
                    await self.twitch_bot.channel.mod(task.data['user_name'])
                    await self.discord_bot.send_log(f"Added Twitch Moderator | {task.data['user_input'] if 'user_input' in task.data else task.data['user_name']}")
                    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    with open('Twitch/data/rewards/moderators.txt', 'a+') as f:
                        f.write(f'{time_now}|{task.data["user_name"]}\n')
                    
                elif task.action == self.task_queue.TASK_TW_ADD_VIP:
                    await self.twitch_bot.channel.vip(task.data['user_name'])
                    await self.discord_bot.send_log(f"Added Twitch VIP | {task.data['user_input'] if 'user_input' in task.data else task.data['user_name']}")
                    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    with open('Twitch/data/rewards/vips.txt', 'a+') as f:
                        f.write(f'{time_now}|{task.data["user_name"]}\n')
                    
                elif task.action == self.task_queue.TASK_TW_TIMEOUT:
                    for rwd in self.config['twitch']['rewards']:
                        if rwd['name'].lower() == task.data['reward_name'].lower():
                            duration = rwd['time']
                            await self.twitch_bot.channel.timeout(
                                timeout_id = task.data['user_input'] if 'user_input' in task.data else task.data['user_name'],
                                duration = duration,
                                reason = f'ValkyrieBot | {task.data["user_name"]} has timed you out for {task.data["reward_cost"]} Divine Potions!'
                            )
                            await self.discord_bot.send_log(f"Timed out Twitch User | {task.data['user_input'] if 'user_input' in task.data else task.data['user_name']} | {duration} seconds")
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
                    
                self.logger.info(f'Executing task from queue | {i+1}/{q} | {task.action} | {task.data}')
    
    async def run(self):
        """
        A loop which runs the main bot methods every N seconds. The N seconds interval is defined in the configuration
        file.
        """
        while True:
            start_time = datetime.datetime.now()
            
            await self.check_unmod()
            await self.check_queue()
            await self.check_live()

            interval_miliseconds = self.config['interval'] * 1000 if self.ready else 10000
            time_microseconds = (datetime.datetime.now() - start_time).microseconds
            await asyncio.sleep((interval_miliseconds - time_microseconds) / 1000000)
