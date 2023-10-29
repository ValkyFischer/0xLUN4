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

from twitchio.ext import commands, pubsub

from Twitch.auth import Auth
from Twitch.channel import Channel
from Twitch.commands import Commands
from Twitch.events import Event
from Twitch.stream import Stream

from ValkyrieUtils.Logger import ValkyrieLogger

from Modules.luna import Luna
from Modules.tasks import TaskQueue


class TwitchBot(commands.Bot):
    """
    A Twitch bot that can be used to check if a channel is live or not. It utilizes the Twitch API to check if a channel
    is live or not. It also has a few commands that can be used in chat.
    
    Args:
        config (dict): The configuration dictionary.
        logger (ValkyrieLogger): The logger.
        task_queue (TaskQueue): The queue instance.
    """
    def __init__(self, config: dict, logger: ValkyrieLogger, task_queue: TaskQueue):
        self.loaded = False
        self.logger = logger
        self.config = config
        self.task_queue = task_queue
        self.stream = Stream(self.config, self.logger)
        self.channel = Channel(self.config, self.logger, self.stream)
        self.auth = Auth(self.config, self.logger)
        self.luna = Luna(self.logger, self.config)
        prefix = self.config['twitch']['prefix']
        scopes = [
            "analytics:read:extensions",
            "user:edit",
            "user:read:email",
            "clips:edit",
            "bits:read",
            "analytics:read:games",
            "user:edit:broadcast",
            "user:read:broadcast",
            "chat:read",
            "chat:edit",
            "channel:moderate",
            "channel:read:subscriptions",
            "whispers:read",
            "whispers:edit",
            "moderation:read",
            "channel:read:redemptions",
            "channel:edit:commercial",
            "channel:read:hype_train",
            "channel:read:stream_key",
            "channel:manage:extensions",
            "channel:manage:broadcast",
            "user:edit:follows",
            "channel:manage:redemptions",
            "channel:read:editors",
            "channel:manage:videos",
            "user:read:blocked_users",
            "user:manage:blocked_users",
            "user:read:subscriptions",
            "user:read:follows",
            "channel:manage:polls",
            "channel:manage:predictions",
            "channel:read:polls",
            "channel:read:predictions",
            "moderator:manage:automod",
            "channel:manage:schedule",
            "channel:read:goals",
            "moderator:read:automod_settings",
            "moderator:manage:automod_settings",
            "moderator:manage:banned_users",
            "moderator:read:blocked_terms",
            "moderator:manage:blocked_terms",
            "moderator:read:chat_settings",
            "moderator:manage:chat_settings",
            "channel:manage:raids",
            "moderator:manage:announcements",
            "moderator:manage:chat_messages",
            "user:manage:chat_color",
            "channel:manage:moderators",
            "channel:read:vips",
            "channel:manage:vips",
            "user:manage:whispers",
            "channel:read:charity",
            "moderator:read:chatters",
            "moderator:read:shield_mode",
            "moderator:manage:shield_mode",
            "moderator:read:shoutouts",
            "moderator:manage:shoutouts",
            "moderator:read:followers",
            "channel:read:guest_star",
            "channel:manage:guest_star",
            "moderator:read:guest_star",
            "moderator:manage:guest_star"
        ]
        channels = [f"#{self.channel.name}"]
        bot_token = self.auth.authorize(self.config['twitch']['client_id'], self.config['twitch']['client_secret'], self.config['twitch']['redirect_uri'], scopes)
        super().__init__(token = bot_token, prefix = prefix, initial_channels = channels)
        
        self.pubsub = pubsub.PubSubPool(self)
        self.event_handler = Event(self)
        self.cmd_handler = Commands(self)

    # ==================================================================================================================
    # Events
    # ==================================================================================================================

    async def event_ready(self):
        """
        This event is called once when the bot goes online.
        """
        await self.event_handler.on_ready()

    async def event_pubsub_bits(self, event: pubsub.PubSubBitsMessage):
        """
        This event is called when a user cheers bits in chat.
        """
        await self.event_handler.on_bits(event)
    
    async def event_pubsub_channel_points(self, event: pubsub.PubSubChannelPointsMessage):
        """
        This event is called when a user redeems a channel point reward in chat.
        """
        await self.event_handler.on_channel_points(event)
    
    async def event_pubsub_channel_subscriptions(self, event: pubsub.PubSubChannelSubscribe):
        """
        This event is called when a user subscribes to the channel.
        """
        await self.event_handler.on_subscriptions(event)

    # ==================================================================================================================
    # Commands
    # ==================================================================================================================

    @commands.command(name = "ping")
    async def tw_ping(self, ctx: commands.Context):
        """
        A command that can be used to check the latency of the bot.
        """
        await self.cmd_handler.do_ping(ctx)

    @commands.command(name = "discord")
    async def tw_discord(self, ctx: commands.Context):
        """
        A command that can be used to get the Discord invite link.
        """
        await self.cmd_handler.do_discord(ctx)
        
    @commands.command(name = "exval")
    async def tw_exval(self, ctx: commands.Context):
        """
        A command that can be used to get the ExVal Limited link.
        """
        await self.cmd_handler.do_exval(ctx)
        
    @commands.command(name = "translate")
    async def tw_translate(self, ctx: commands.Context, *, text: str):
        """
        A command that can be used to translate text using Luna.
        """
        await self.cmd_handler.do_translate(ctx, text)
        
    @commands.command(name = "ask")
    async def tw_ask(self, ctx: commands.Context, *, text: str):
        """
        A command that can be used to ask Luna a question.
        """
        await self.cmd_handler.do_ask(ctx, text)
        
    @commands.command(name = "set_title")
    async def tw_set_title(self, ctx: commands.Context, *, title: str):
        """
        *Mod Only!* - A command that can be used to set the title of the stream.
        """
        await self.cmd_handler.do_set_title(ctx, title)
    
    @commands.command(name = "set_game")
    async def tw_set_game(self, ctx: commands.Context, *, game: str):
        """
        *Mod Only!* - A command that can be used to set the game of the stream.
        """
        await self.cmd_handler.do_set_game(ctx, game)
        
    @commands.command(name = "design_doc")
    async def tw_design_doc(self, ctx: commands.Context):
        """
        A command that can be used to get the game design document.
        """
        await self.cmd_handler.do_design_doc(ctx)
    
    @commands.command(name = "manual_doc")
    async def tw_manual_doc(self, ctx: commands.Context):
        """
        A command that can be used to get the game manual document.
        """
        await self.cmd_handler.do_manual_doc(ctx)
