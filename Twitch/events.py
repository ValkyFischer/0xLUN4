#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky

--------

About:
    This script provides the functionality for the Twitch bot to handle events.

"""
import random
from twitchio.ext import pubsub

from Modules.tasks import Task


class Event:
    """
    A class to handle events. The event can be any object that is received from Twitch and the Twitch PubSub system.
    """
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.logger = bot.logger
        self.channel = bot.channel
        self.pubsub = bot.pubsub
    
    async def on_ready(self):
        """
        This event is called once when the bot goes online. It is used to setup the bot and to subscribe to topics.
        """
        token = self.config['twitch']['user']['token']
        
        try:
            await self.channel.setup()
            
        except Exception as e:
            self.logger.error(f'Failed to populate channel: {str(e)}')
        
        try:
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
        
        self.logger.info(f'Twitch logged in as {self.channel.name}')
        self.logger.info(f'Twitch account id is {self.channel.id}')
        self.bot.loaded = True
    
    async def on_bits(self, event: pubsub.PubSubBitsMessage):
        """
        This event is called when a user cheers bits.
        
        Args:
            event (pubsub.PubSubBitsMessage): The event.
        """
        pass  # TODO: Implement this
    
    async def on_channel_points(self, event: pubsub.PubSubChannelPointsMessage):
        """
        This event is called when a user redeems a channel point reward. It creates and puts a new task into the
        task queue. The task queue is used to queue tasks that are related to both, Discord or Twitch.
        
        Args:
            event (pubsub.PubSubChannelPointsMessage): The event.
        """
        # uuid = event.id
        # status = event.status
        # channel_id = event.channel_id
        # timestamp = event.timestamp
        # user_id = event.user.id
        user_name = event.user.name
        user_input = " | " + event.input if event.input else ""
        reward_name = event.reward.title
        # reward_uuid = event.reward.id
        reward_cost = event.reward.cost
        
        self.logger.info(f'Twitch Channel Points | {user_name} | {reward_name} ({reward_cost}){user_input}')
        
        for reward in self.config['twitch']['rewards']:
            if reward['name'].lower() == reward_name.lower():
                task_action = reward['task']
                task_instant = reward['instant']
                task_data = {
                    "user_name": user_name,
                    "reward_name": reward_name,
                    "reward_cost": reward_cost,
                    "user_input": event.input,
                }
                task = Task(task_action, task_data, task_instant)
                self.bot.task_queue.add_task(task)
        
        channel = self.bot.get_channel(user_name)
        if channel is not None:
            random_emote = random.choice(self.channel.emotes)
            await channel.send(f'[CHANNEL POINTS] {user_name} redeemed "{reward_name}"{user_input} {random_emote}')
    
    async def on_subscriptions(self, event: pubsub.PubSubChannelSubscribe):
        """
        This event is called when a user subscribes to the channel.
        
        Args:
            event (pubsub.PubSubChannelSubscribe): The event.
        """
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
        
        channel = self.bot.get_channel(user_name)
        if channel is not None:
            random_emote = random.choice(self.channel.emotes)
            if is_gift:
                await channel.send(
                    f'[SUBSCRIPTION] {user_name} gifted a {tier_name} to {recipient_name} {random_emote}')
            else:
                await channel.send(
                    f'[SUBSCRIPTION] {user_name} got a {tier_name}. They are subscribed for {length} month{"s" if int(length) > 1 else ""}{message} {random_emote}')
