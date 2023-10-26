import asyncio
import datetime

from ValkyrieUtils.Logger import ValkyrieLogger
from bot_discord import DiscordBot
from bot_twitch import TwitchBot
from tasks import TaskQueue


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
    
    async def check_queue(self):
        """
        A method which checks the queue for tasks. If a task is found, it will be executed.
        """
        if self.task_queue.tasks.empty():
            if not self.empty:
                self.empty = True
                self.logger.info(f'Observing task queue is empty')
        else:
            self.empty = False
            task = await self.task_queue.get_task()
            self.logger.info(f'Executing task from queue | {task.action} | {task.data}')
    
    async def run(self):
        """
        A loop which runs the main bot methods every N seconds. The N seconds interval is defined in the configuration
        file.
        """
        while True:
            start_time = datetime.datetime.now()

            await self.check_queue()
            await self.check_live()

            interval_miliseconds = self.config['interval'] * 1000 if self.ready else 10000
            time_microseconds = (datetime.datetime.now() - start_time).microseconds
            await asyncio.sleep((interval_miliseconds - time_microseconds) / 1000000)
