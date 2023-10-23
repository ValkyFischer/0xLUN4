#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky

--------

About:
    This script is a Discord bot that can be used to send notifications to a Discord server. The bot uses the Discord
    API to send notifications and to use slash commands. The bot also uses the Twitch API to check if a channel is live
    or not. The bot will send a notification to the Discord server when a channel goes live or offline.

--------

Example:
    To use this Discord bot, you can interact with it in your Discord server. Here are some example commands:
    
    1. Check the bot's latency:
       >> /ping
       This command will show the bot's latency in milliseconds.
            
    2. Get the Discord invite link:
       >> /discord
       This command will provide you with the Discord invite link to join the community.
            
    3. Get the Twitch channel link:
       >> /twitch
       This command will provide you with a link to the Twitch channel.
            
    4. Get the ExVal Limited link:
       >> /exval
       This command will provide you with a link to the official website of ExVal Ltd.
    
"""

import asyncio
import datetime
import logging
import discord

from discord import app_commands
from bot_twitch import TwitchBot


class DiscordBot:
    """
    A Discord bot that can be used to send notifications to a Discord server. The bot uses the Discord API to send
    notifications and to use slash commands. The bot also uses the Twitch API to check if a channel is live or not.
    
    Args:
        config (dict): The configuration dictionary.
        logger (logging.Logger): The logger.
        twitch_bot (TwitchBot): The Twitch bot object.
    """
    def __init__(self, config: dict, logger: logging.Logger, twitch_bot: TwitchBot):
        self.logger = logger
        self.config = config
        self.token = self.config['discord']['bot_token']
        self.guild_id = self.config['discord']['guild_id']
        self.activity = discord.Activity(name="Tests", type=5)
        self.intents = discord.Intents.all()
        self.client = discord.Client(intents=self.intents, activity=self.activity)
        self.tree = app_commands.CommandTree(self.client)
        self.guild = discord.Object(id=self.guild_id)
        
        self.twitch_bot = twitch_bot
        
        self.ch_admin = None
        self.ch_cmd = None
        self.ch_stream = None
    
    async def check_live_loop(self):
        """
        A loop which checks every 60 seconds if a channel is live or not. If a channel goes live or offline, a
        notification will be sent to the Discord server.
        """
        await asyncio.sleep(10)
        while True:
            start_time = datetime.datetime.now()
            for channel in self.config['twitch']['channels'].keys():
                is_live = await self.twitch_bot.check_live(channel)
                old_status = self.config['twitch']['channels'].get(channel)
                if old_status is None:
                    self.config['twitch']['channels'][channel] = is_live
                if old_status != is_live:
                    if is_live:
                        await self.send_notification(f'{channel}')
                        self.logger.info(f'Channel went live | {channel}')
                    else:
                        await self.send_log(f'{channel} went offline')
                        self.logger.info(f'Channel went offline | {channel}')
                    self.config['twitch']['channels'][channel] = is_live
                self.logger.info(f'{channel} is live: {is_live}')

            interval_miliseconds = self.config['discord']['interval'] * 1000
            time_microseconds = (datetime.datetime.now() - start_time).microseconds
            await asyncio.sleep((interval_miliseconds - time_microseconds) / 1000000)
    
    async def send_log(self, message: str):
        """
        Sends a message to the admin channel. The message will be formatted as a simple message with a [LOG] prefix.
        
        Args:
            message (str): The message to send.
        """
        if self.ch_admin:
            await self.ch_admin.send(f"[LOG] {message}")
    
    async def send_notification(self, channel: str):
        """
        Sends a message to the stream channel. The message will be formatted as an embed message.
        
        Args:
            channel (str): The channel that went live.
        """
        await self.send_log(f'{channel} went live')
        # TODO: Proper embedded message
        #       await self.ch_stream.send(message)

    def setup(self):
        """
        Sets up the Discord bot. This method will be called before the bot starts, adds all slash commands
        to the bot, and will set up the on_ready event.
        
        The following commands will be added:
            - ping
            - discord
            - twitch
            - exval
        """
        @self.client.event
        async def on_ready():
            """
            This event is called once when the bot goes online.
            """
            await self.tree.sync(guild=self.guild)
            self.logger.info(f'Discord Bot logged in as {self.client.user}')
            self.logger.info(f'Discord Bot user id is {self.client.user.id}')
            self.logger.info(f'Discord Bot joined {len(self.client.guilds)} Discords')
            self.ch_admin = self.client.get_channel(int(self.config['discord']['channels'].get("admin")))
            self.ch_cmd = self.client.get_channel(int(self.config['discord']['channels'].get("commands")))
            self.ch_stream = self.client.get_channel(int(self.config['discord']['channels'].get("stream")))
            self.client.loop.create_task(self.check_live_loop())
            self.logger.info(f'Discord Bot loaded all tasks')
            self.logger.info('=' * 103)
        
        # ==============================================================================================================
        # Commands
        # ==============================================================================================================
        
        @self.tree.command(name="ping", description="Test Bot Latency", guild=self.guild)
        async def dc_ping(interaction):
            """
            This command will show the bot's latency in milliseconds.
            
            Args:
                interaction (any): The interaction object.
            """
            self.logger.info(f'Discord Command | ping | {interaction.user.name}')
            await interaction.response.send_message(f"[PING] Pong! | {round(self.client.latency * 1000)}ms")
        
        @self.tree.command(name="discord", description="Discord Invite Link", guild=self.guild)
        async def dc_discord(interaction):
            """
            This command will provide you with the Discord invite link to join the community.
            
            Args:
                interaction (any): The interaction object.
            """
            self.logger.info(f'Discord Command | discord | {interaction.user.name}')
            await interaction.response.send_message(f"[DISCORD] You can use the following link to invite your friends. |  https://discord.gg/vky")
        
        @self.tree.command(name="twitch", description="Twitch Channel Link", guild=self.guild)
        async def dc_twitch(interaction):
            """
            This command will provide you with a link to the Twitch channel.
            
            Args:
                interaction (any): The interaction object.
            """
            self.logger.info(f'Discord Command | twitch | {interaction.user.name}')
            await interaction.response.send_message(f"[TWITCH] Want to watch Valky live? Follow on Twitch and dont miss the next stream. | https://twitch.tv/v_lky")
        
        @self.tree.command(name="exval", description="ExVal Limited Link", guild=self.guild)
        async def dc_exval(interaction):
            """
            This command will provide you with a link to the official website of ExVal Ltd.
            
            Args:
                interaction (any): The interaction object.
            """
            self.logger.info(f'Discord Command | exval | {interaction.user.name}')
            await interaction.response.send_message(f"[EXVAL] Want to know more about ExVal Limited? Check out the official website of ExVal Ltd. | https://exv.al/en")
            