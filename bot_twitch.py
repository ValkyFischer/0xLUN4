#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky

--------

About:
    This script is a Twitch bot that can be used to check if a channel is live or not. It utilizes the Twitch API
    to check if a channel is live or not. It also has a few commands that can be used in chat.

--------

Example:
    To use this Twitch bot, you can interact with it in your Twitch chat. Here are some example commands:

    1. Check the bot's latency:
       >> ping
       This command will show the bot's latency in milliseconds.

    2. Get the Discord invite link:
       >> discord
       This command will provide you with the Discord invite link to join the community.

    3. Get the ExVal Limited link:
       >> exval
       This command will provide you with a link to the official website of ExVal Ltd.

"""

import datetime
import json
import logging
import aiohttp

from twitchio.ext import commands
from ValkyrieUtils.Tools import ValkyrieTools
from luna import Luna

LUNA: Luna = None


class TwitchBot(commands.Bot):
    """
    A Twitch bot that can be used to check if a channel is live or not. It utilizes the Twitch API to check if a channel
    is live or not. It also has a few commands that can be used in chat.
    
    Args:
        config (dict): The configuration dictionary.
        logger (logging.Logger): The logger.
    """
    def __init__(self, config: dict, logger: logging.Logger):
        self.logger = logger
        self.config = config
        prefix = self.config['twitch']['prefix']
        bot_token = self.config['twitch']['bot_token']
        channels = [f"#{x}" for x in self.config['twitch']['channels']]
        super().__init__(token = bot_token, prefix = prefix, initial_channels = channels)
        
        global LUNA
        LUNA = Luna(self.logger, self.config)

    async def event_ready(self):
        """
        This event is called once when the bot goes online.
        """
        self.logger.info(f'Twitch Bot logged in as {self.nick}')
        self.logger.info(f'Twitch Bot user id is {self.user_id}')
        self.logger.info(f'Twitch Bot joined {len(self.config["twitch"]["channels"])} Channels')
        self.logger.info('=' * 103)

    async def check_live(self, user_name: str) -> bool:
        """
        Checks if a channel is live or not.
        
        Args:
            user_name (str): The name of the channel.
            
        Returns:
            bool: True if the channel is live, False if the channel is offline.
        """
        user_id = await self._get_user_id(user_name)
        is_live = await self._get_user_status(user_id)
        return is_live

    async def _get_user_id(self, username: str) -> int:
        """
        Gets the user id of a channel.
        
        Args:
            username (str): The name of the channel.
            
        Returns:
            int: The user id of the channel.
        """
        async with aiohttp.ClientSession() as session:
            url = f'https://api.twitch.tv/helix/users?login={username}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                return int(response_data.get('data')[0].get('id'))
            
    async def _get_user_status(self, user_id: int) -> bool:
        """
        Gets the status of a channel.
        
        Args:
            user_id (int): The user id of the channel.
            
        Returns:
            bool: True if the channel is live, False if the channel is offline.
        """
        async with aiohttp.ClientSession() as session:
            url = f'https://api.twitch.tv/helix/streams?user_id={str(user_id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                if response_data.get('data'):
                    return True
                return False

    # ==================================================================================================================
    # Commands
    # ==================================================================================================================

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """
        A command that can be used to check the latency of the bot.
        
        Args:
            ctx (commands.Context): The context of the command.
        """
        self.logger.info(f'Twitch Command | ping | {ctx.author.name}')
        msg_time = datetime.datetime.utcnow()
        await ctx.send(f'[PING] Pong! | {round((msg_time - ctx.message.timestamp).total_seconds()) * 100}ms')

    @commands.command()
    async def discord(self, ctx: commands.Context):
        """
        A command that can be used to get the Discord invite link.
        
        Args:
            ctx (commands.Context): The context of the command.
        """
        self.logger.info(f'Twitch Command | discord | {ctx.author.name}')
        await ctx.send(f'[DISCORD] Want to ask something specific? Want to know more about Valky? Join the Discord community! | https://discord.gg/vky')
        
    @commands.command()
    async def exval(self, ctx: commands.Context):
        """
        A command that can be used to get the ExVal Limited link.
        
        Args:
            ctx (commands.Context): The context of the command.
        """
        self.logger.info(f'Twitch Command | exval | {ctx.author.name}')
        await ctx.send(f'[EXVAL] Want to know more about ExVal Limited? Check out the official website of ExVal Ltd. | https://exv.al/en')
        
    @commands.command()
    async def translate(self, ctx: commands.Context, *, text: str):
        """
        A command that can be used to translate text using Luna.
        
        Args:
            ctx (commands.Context): The context of the command.
            text (str): The text to translate.
        """
        self.logger.info(f'Twitch Command | translate | {ctx.author.name}')
        try:
            response = await LUNA.lunaTranslate(text)
        except Exception as e:
            self.logger.error(f'Failed to make the request: {str(e)}')
            response = {
                "msg": "Command failed",
                "Return": False,
                "ReturnCode": 0,
                "data": {
                    "message": "Command failed"
                }
            }
        await ctx.send(f'[LUNA] {response["data"]}')
        
    @commands.command()
    async def ask(self, ctx: commands.Context, *, text: str):
        """
        A command that can be used to ask Luna a question.
        
        Args:
            ctx (commands.Context): The context of the command.
            text (str): The question to ask.
        """
        self.logger.info(f'Twitch Command | ask | {ctx.author.name}')
        try:
            response = await LUNA.lunaAsk(text)
        except Exception as e:
            self.logger.error(f'Failed to make the request: {str(e)}')
            response = {
                "msg": "Command failed",
                "Return": False,
                "ReturnCode": 0,
                "data": {
                    "message": "Command failed"
                }
            }
        await ctx.send(f'[LUNA] {response["data"]}')
