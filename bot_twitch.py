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

import logging
import random

from twitchio.ext import commands, pubsub

from Twitch.auth import Auth
from Twitch.channel import Channel
from Twitch.stream import Stream
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
        self.stream = Stream()
        self.channel = Channel(self.config, self.logger, self.stream)
        self.auth = Auth(self.config, self.logger)
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
        if self.config['twitch']['bot_token'] is None or self.config['twitch']['bot_token'] == "":
            bot_token = self.auth.authorize(self.config['twitch']['client_id'], self.config['twitch']['client_secret'], self.config['twitch']['redirect_uri'], scopes)
        else:
            # TODO: Add a check to see if the bot token is valid
            bot_token = self.config['twitch']['bot_token']
        super().__init__(token = bot_token, prefix = prefix, initial_channels = channels)
        
        self.pubsub = pubsub.PubSubPool(self)
        
        global LUNA
        LUNA = Luna(self.logger, self.config)

    async def event_ready(self):
        """
        This event is called once when the bot goes online.
        """
        self.channel.id = self.user_id
        self.logger.info(f'Twitch logged in as {self.channel.name}')
        self.logger.info(f'Twitch account id is {self.channel.id}')
        token = self.config['twitch']['bot_token']
        
        try:
            await self.channel.setup(self.channel.id)
        except Exception as e:
            self.logger.error(f'Failed to populate channel: {str(e)}')
            
        try:
            # subscribe to bits and channel points
            topics = [
                pubsub.channel_points(token)[self.channel.id],
                pubsub.bits(token)[self.channel.id],
                pubsub.channel_subscriptions(token)[self.channel.id],
                # pubsub.moderation_user_action(token)[self.channel.id]
            ]
            await self.pubsub.subscribe_topics(topics)
            self.logger.info(f'Twitch Topics | Bits, Channel Points, Subscriptions')
            
        except Exception as e:
            self.logger.error(f'Failed to subscribe to topics: {str(e)}')
        self.logger.info('=' * 103)

    async def event_pubsub_bits(self, event: pubsub.PubSubBitsMessage):
        pass  # TODO: Implement this
    
    async def event_pubsub_channel_points(self, event: pubsub.PubSubChannelPointsMessage):
        # get the reward info
        uuid = event.id
        status = event.status
        channel_id = event.channel_id
        timestamp = event.timestamp
        # get the user info
        user_id = event.user.id
        user_name = event.user.name
        user_input = " | " + event.input if event.input else ""
        # get the reward info
        reward_name = event.reward.title
        reward_uuid = event.reward.id
        reward_cost = event.reward.cost
        
        self.logger.info(f'Twitch Channel Points | {user_name} | {reward_name} ({reward_cost}) | {user_input}')
        
        channel = self.get_channel(user_name)
        if channel is not None:
            random_emote = random.choice(self.channel.emotes)
            await channel.send(f'[CHANNEL POINTS] {user_name} redeemed "{reward_name}"{user_input} {random_emote}')
    
    async def event_pubsub_channel_subscriptions(self, event: pubsub.PubSubChannelSubscribe):
        user_name = event.user.name if event.user.name else "Anonymous"
        # user_id = event.user.id
        # tier = event.sub_plan
        tier_name = event.sub_plan_name
        length = event.cumulative_months
        months_multi = " | " + event.multi_month_duration if event.multi_month_duration else ""
        message = " | " + event.message if event.message else ""
        
        is_gift = event.is_gift
        recipient_name = event.recipient.name if is_gift else None
        
        if is_gift:
            self.logger.info(f'Twitch Gift Subscriptions | {user_name} | {tier_name} | {length}{months_multi}{message}')
        else:
            self.logger.info(f'Twitch Subscriptions | {user_name} | {tier_name} | {length}{months_multi}{message}')
        
        channel = self.get_channel(user_name)
        if channel is not None:
            random_emote = random.choice(self.channel.emotes)
            if is_gift:
                await channel.send(f'[SUBSCRIPTION] {user_name} gifted a {tier_name} to {recipient_name} {random_emote}')
            else:
                await channel.send(f'[SUBSCRIPTION] {user_name} got a {tier_name}. They are subscribed for {length} month{"s" if int(length) > 1 else ""}{message} {random_emote}')

    async def check_live(self, user_name: str) -> bool:
        """
        Checks if a channel is live or not.
        
        Args:
            user_name (str): The name of the channel.
            
        Returns:
            bool: True if the channel is live, False if the channel is offline.
        """
        # user_id = await self.channel.get_id(user_name)
        is_live = await self.channel.get_status(self.channel.id)
        return is_live

    # ==================================================================================================================
    # Commands
    # ==================================================================================================================

    @commands.command(name = "ping")
    async def tw_ping(self, ctx: commands.Context):
        """
        A command that can be used to check the latency of the bot.
        
        Args:
            ctx (commands.Context): The context of the command.
        """
        self.logger.info(f'Twitch Command | ping | {ctx.author.name}')
        try:
            response = await LUNA.lunaPing()
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

    @commands.command(name = "discord")
    async def tw_discord(self, ctx: commands.Context):
        """
        A command that can be used to get the Discord invite link.
        
        Args:
            ctx (commands.Context): The context of the command.
        """
        self.logger.info(f'Twitch Command | discord | {ctx.author.name}')
        await ctx.send(f'[DISCORD] Want to ask something specific? Want to know more about Valky? Join the Discord community! | https://discord.gg/vky')
        
    @commands.command(name = "exval")
    async def tw_exval(self, ctx: commands.Context):
        """
        A command that can be used to get the ExVal Limited link.
        
        Args:
            ctx (commands.Context): The context of the command.
        """
        self.logger.info(f'Twitch Command | exval | {ctx.author.name}')
        await ctx.send(f'[EXVAL] Want to know more about ExVal Limited? Check out the official website of ExVal Ltd. | https://exv.al/en')
        
    @commands.command(name = "translate")
    async def tw_translate(self, ctx: commands.Context, *, text: str):
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
        
    @commands.command(name = "ask")
    async def tw_ask(self, ctx: commands.Context, *, text: str):
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
