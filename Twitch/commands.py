#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky

--------

About:
    This script provides the functionality serve commands to the Twitch bot.

"""
import random

from twitchio.ext import commands


class Commands:
    """
    A class to serve commands to the Twitch bot.
    """
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.logger = bot.logger
        self.luna = bot.luna
        self.channel = bot.channel
        self.stream = bot.stream
     
    async def do_ping(self, ctx: commands.Context):
        """
        A command that can be used to check the latency of the bot.

        Args:
            ctx (commands.Context): The context of the command.
        """
        self.logger.info(f'Twitch Command | ping | {ctx.author.name}')
        try:
            response = await self.luna.lunaPing()
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
        
        await ctx.send(f'[PING] Pong! | {response["data"]}ms')
    
    async def do_discord(self, ctx: commands.Context):
        """
        A command that can be used to get the Discord invite link.

        Args:
            ctx (commands.Context): The context of the command.
        """
        self.logger.info(f'Twitch Command | discord | {ctx.author.name}')
        await ctx.send(
            f'[DISCORD] Want to ask something specific? Want to know more about Valky? Join the Discord community! | https://discord.gg/vky')
    
    async def do_exval(self, ctx: commands.Context):
        """
        A command that can be used to get the ExVal Limited link.

        Args:
            ctx (commands.Context): The context of the command.
        """
        self.logger.info(f'Twitch Command | exval | {ctx.author.name}')
        await ctx.send(
            f'[EXVAL] Want to know more about ExVal Limited? Check out the official website of ExVal Ltd. | https://exv.al/en')
    
    async def do_translate(self, ctx: commands.Context, text: str):
        """
        A command that can be used to translate text using Luna.

        Args:
            ctx (commands.Context): The context of the command.
            text (str): The text to translate.
        """
        self.logger.info(f'Twitch Command | translate | {ctx.author.name}')
        try:
            response = await self.luna.lunaTranslate(text)
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
    
    async def do_ask(self, ctx: commands.Context, text: str):
        """
        A command that can be used to ask Luna a question.

        Args:
            ctx (commands.Context): The context of the command.
            text (str): The question to ask.
        """
        self.logger.info(f'Twitch Command | ask | {ctx.author.name}')
        try:
            response = await self.luna.lunaAsk(text)
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
    
    async def do_set_title(self, ctx: commands.Context, title: str):
        """
        A command that can be used to set the title of the stream.

        Args:
            ctx (commands.Context): The context of the command.
            title (str): The title of the stream.
        """
        self.logger.info(f'Twitch Command | set_title | {ctx.author.name} | {title}')
        random_emote = random.choice(self.channel.emotes)
        if ctx.author.is_mod:
            await self.stream.set_info(user_id = self.channel.id, title = title)
            await ctx.send(f'[TITLE] {title} | {ctx.author.name} {random_emote}')
        else:
            await ctx.send(
                f'[TITLE] You do not have permission to use this command! | {ctx.author.name} {random_emote}')
    
    async def do_set_game(self, ctx: commands.Context, game: str):
        """
        A command that can be used to set the game of the stream.

        Args:
            ctx (commands.Context): The context of the command.
            game (str): The game of the stream.
        """
        self.logger.info(f'Twitch Command | set_game | {ctx.author.name} | {game}')
        random_emote = random.choice(self.channel.emotes)
        if ctx.author.is_mod:
            await self.stream.set_info(user_id = self.channel.id, game_name = game)
            await ctx.send(f'[GAME] {game} | {ctx.author.name} {random_emote}')
        else:
            await ctx.send(f'[GAME] You do not have permission to use this command! | {ctx.author.name} {random_emote}')
            
    async def do_design_doc(self, ctx: commands.Context):
        """
        A command that can be used to get the design document.

        Args:
            ctx (commands.Context): The context of the command.
        """
        self.logger.info(f'Twitch Command | design_doc | {ctx.author.name}')
        await ctx.send(f'[ARIA: Live] Find the game design document here: https://1drv.ms/w/s!AjIdyV70_rGwhYBcTzLniJqWQxXcNw')
    
    async def do_manual_doc(self, ctx: commands.Context):
        """
        A command that can be used to get the manual document.
        
        Args:
            ctx (commands.Context): The context of the command.
        """
        self.logger.info(f'Twitch Command | manual_doc | {ctx.author.name}')
        await ctx.send(f'[ARIA: Live] Find the game manual document here: https://1drv.ms/w/s!AjIdyV70_rGwhYBfM6N-W2l4tuoneQ')
