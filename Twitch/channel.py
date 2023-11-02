#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky

--------

About:
    This script provides the functionality to get and set the stream information of a channel.
    
"""
import logging
import aiohttp


class Channel:
    """
    A class used to represent a Twitch channel. This class will store the name, id, emotes, followers, subscribers,
    VIPs, moderators, and stream information of a channel.
    
    Args:
        config (dict): The configuration file.
        logger (logging.Logger): The logger.
        
    Properties:
        - name (str): The name of the channel.
        - id (int): The id of the channel.
        - is_live (bool): True if the channel is live, False if the channel is offline.
        - emotes (list): A list of emotes.
        - followers (list): A list of followers.
        - subscribers (list): A list of subscribers.
        - vips (list): A list of VIPs.
        - moderators (list): A list of moderators.
        - stream (Stream): The stream information of the channel.
    """
    def __init__(self, config: dict, logger: logging.Logger, stream):
        self.config = config
        self.logger = logger
        self.name = self.config['twitch']['channel']
        self.id = 0
        self.is_live = False
        self.emotes = []
        self.followers = []
        self.follower_count = 0
        self.subscribers = []
        self.subscriber_count = 0
        self.vips = []
        self.moderators = []
        self.banned = []
        self.stream = stream
        
    async def setup(self) -> None:
        """
        Sets up the channel by getting the emotes, followers, subscribers, VIPs, moderators, and stream information.
        """
        # get the user id of the channel
        if not self.id or self.id <= 0 or self.id is None:
            self.id = await self.get_id(self.name)
            
        # get the emotes of the channel
        emotes = await self.get_emotes()
        for emote in emotes:
            if emote.get('name') not in self.emotes:
                self.emotes.append(emote.get('name'))
        self.logger.info(f'Twitch Emotes | {len(self.emotes)}')
        
        # get the followers of the channel
        followers = await self.get_followers()
        self.follower_count = await self.get_followers(True)
        for follower in followers:
            if follower.get('user_name') not in self.followers:
                self.followers.append(follower.get('user_name')) if follower.get('user_name').lower() != self.name.lower() else None
        self.logger.info(f'Twitch Followers | {self.follower_count} | {len(self.followers)}')
        
        # get the subscribers of the channel
        subscribers = await self.get_subscribers()
        self.subscriber_count = await self.get_subscribers(True)
        for subscriber in subscribers:
            if subscriber.get('user_name') not in self.subscribers:
                self.subscribers.append(subscriber.get('user_name')) if subscriber.get('user_name').lower() != self.name.lower() else None
        self.logger.info(f'Twitch Subscribers | {self.subscriber_count} | {len(self.subscribers)}')
        
        # get the VIPs of the channel
        vips = await self.get_vips()
        for vip in vips:
            if vip.get('user_name') not in self.vips:
                self.vips.append(vip.get('user_name')) if vip.get('user_name').lower() != self.name.lower() else None
        self.logger.info(f'Twitch VIPs | {len(self.vips)}')
        
        # get the moderators of the channel
        moderators = await self.get_moderators()
        for moderator in moderators:
            if moderator.get('user_name') not in self.moderators:
                self.moderators.append(moderator.get('user_name')) if moderator.get('user_name').lower() != self.name.lower() else None
        self.logger.info(f'Twitch Moderators | {len(self.moderators)}')
        
        # get the bans of the channel
        bans = await self.get_bans()
        for ban in bans:
            if ban.get('user_name') not in self.banned:
                self.banned.append(ban.get('user_name')) if ban.get('user_name').lower() != self.name.lower() else None
        self.logger.info(f'Twitch Bans | {len(self.banned)}')
        
        # get the stream information of the channel
        info = await self.stream.get_info(self.id)
        
        self.stream.title = info.get('title')
        self.stream.game.name = info.get('game_name')
        self.stream.game.id = info.get('game_id')
        self.stream.tags = info.get('tags')
        self.stream.language = info.get('broadcaster_language')
        self.stream.classification = info.get('content_classification_labels')
        
        self.logger.info(f'Twitch Stream | Title: {self.stream.title} | Game: {self.stream.game.name} | Language: {self.stream.language}')
    
    # ==================================================================================================================
    # Getters
    # ==================================================================================================================

    async def get_id(self, username: str) -> int:
        """
        Gets the user id of a channel.
        
        Args:
            username (str): The name of the channel.
            
        Returns:
            int: The user id of the channel.
        """
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/users?login={username}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                return int(response_data.get('data')[0].get('id'))
            
    async def get_status(self) -> bool:
        """
        Gets the status of a channel.
            
        Returns:
            bool: True if the channel is live, False if the channel is offline.
        """
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/streams?user_id={str(self.id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                if response_data.get('data'):
                    return True
                return False
            
    async def get_emotes(self) -> list:
        """
        Gets the emotes of a channel.
            
        Returns:
            list: A list of emotes.
        """
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/chat/emotes?broadcaster_id={str(self.id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data.get('data')
    
    async def get_followers(self, total: bool = False) -> list:
        """
        Gets the followers of a channel.
        
        Args:
            total (bool): True if the total number of followers should be returned, False if the list of followers
                should be returned.
            
        Returns:
            list: A list of all followers or the total number of followers.
        """
        async with aiohttp.ClientSession() as session:
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            if total:
                url = f'{self.config["twitch"]["api_uri"]}/channels/followers?broadcaster_id={str(self.id)}'
                async with session.get(url, headers=headers) as resp:
                    response_data = await resp.json()
                    return response_data.get('total')
            
            url = f'{self.config["twitch"]["api_uri"]}/channels/followers?broadcaster_id={str(self.id)}&first=100'
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                followers = response_data.get('data')
                cursor = response_data.get('pagination').get('cursor')
                while cursor:
                    url = f'{self.config["twitch"]["api_uri"]}/channels/followers?broadcaster_id={str(self.id)}&first=100&after={cursor}'
                    async with session.get(url, headers=headers) as resp:
                        response_data = await resp.json()
                        followers.extend(response_data.get('data'))
                        cursor = response_data.get('pagination').get('cursor')
                return followers
    
    async def get_subscribers(self, total: bool = False) -> list:
        """
        Gets the subscribers of a channel.
        
        Args:
            total (bool): True if the total number of subscribers should be returned, False if the list of subscribers
                should be returned.
            
        Returns:
            list: A list of all subscribers or the total number of subscribers.
        """
        async with aiohttp.ClientSession() as session:
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            if total:
                url = f'{self.config["twitch"]["api_uri"]}/subscriptions?broadcaster_id={str(self.id)}'
                async with session.get(url, headers=headers) as resp:
                    response_data = await resp.json()
                    return response_data.get('total')
            
            url = f'{self.config["twitch"]["api_uri"]}/subscriptions?broadcaster_id={str(self.id)}&first=100'
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                subscribers = response_data.get('data')
                cursor = response_data.get('pagination').get('cursor')
                while cursor:
                    url = f'{self.config["twitch"]["api_uri"]}/subscriptions?broadcaster_id={str(self.id)}&first=100&after={cursor}'
                    async with session.get(url, headers=headers) as resp:
                        response_data = await resp.json()
                        subscribers.extend(response_data.get('data'))
                        cursor = response_data.get('pagination').get('cursor')
                return subscribers
    
    async def get_moderators(self) -> list:
        """
        Gets the moderators of a channel.
            
        Returns:
            list: A list of moderators.
        """
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/moderation/moderators?broadcaster_id={str(self.id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data.get('data')
    
    async def get_vips(self) -> list:
        """
        Gets the VIPs of a channel.
        
        Returns:
            list: A list of VIPs.
        """
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/channels/vips?broadcaster_id={str(self.id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data.get('data')
    
    async def get_bans(self) -> list:
        """
        Gets the bans of a channel.
        
        Returns:
            list: A list of bans.
        """
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/moderation/banned?broadcaster_id={str(self.id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data.get('data')
            
    # ==================================================================================================================
    # Setters
    # ==================================================================================================================
    
    async def mod(self, mod_id: int | str) -> None:
        """
        Adds a moderator to a channel.
        
        Args:
            mod_id (int | str): A user id to add as moderators.
        """
        if isinstance(mod_id, str):
            mod_id = await self.get_id(mod_id)
            
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/moderation/moderators?broadcaster_id={str(self.id)}&user_id={mod_id}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.post(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data
    
    async def unmod(self, mod_id: int | str) -> None:
        """
        Removes a moderator from a channel.
        
        Args:
            mod_id (int | str): A user id to remove as moderators.
        """
        if isinstance(mod_id, str):
            mod_id = await self.get_id(mod_id)
            
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/moderation/moderators?broadcaster_id={str(self.id)}&user_id={mod_id}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.delete(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data
    
    async def vip(self, vip_id: int | str) -> None:
        """
        Adds a VIP to a channel.
        
        Args:
            vip_id (int | str): A user id to add as VIPs.
        """
        if isinstance(vip_id, str):
            vip_id = await self.get_id(vip_id)
            
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/channels/vips?broadcaster_id={str(self.id)}&user_id={vip_id}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.post(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data
    
    async def unvip(self, vip_id: int | str) -> None:
        """
        Removes a VIP from a channel.
        
        Args:
            vip_id (int | str): A user id to remove as VIP.
        """
        if isinstance(vip_id, str):
            vip_id = await self.get_id(vip_id)
            
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/channels/vips?broadcaster_id={str(self.id)}&user_id={vip_id}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.delete(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data
    
    async def timeout(self, timeout_id: int | str, duration: int = 600, reason: str = "VALKBOT_NO_REASON") -> None:
        """
        Times out a user in a channel.
        
        Args:
            timeout_id (int | str): A user id to timeout.
            duration (int): The duration of the timeout in seconds.
            reason (str): The reason for the timeout.
        """
        if isinstance(timeout_id, str):
            timeout_id = await self.get_id(timeout_id)
            
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/moderation/bans?broadcaster_id={str(self.id)}&moderator_id={str(self.id)}&user_id={timeout_id}'
            data = {
                "data": {
                    'user_id': timeout_id,
                    'duration': duration,
                    'reason': reason
                }
            }
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}',
                'Content-Type': 'application/json'
            }
            async with session.post(url, headers=headers, json=data) as resp:
                response_data = await resp.json()
                return response_data
    
    async def untimeout(self, timeout_id: int | str) -> None:
        """
        Removes a timeout from a channel.
        
        Args:
            timeout_id (int | str): A user id to remove the timeout.
        """
        if isinstance(timeout_id, str):
            timeout_id = await self.get_id(timeout_id)
            
        await self.unban(timeout_id)
    
    async def ban(self, ban_id: int | str, reason: str = "VALKBOT_NO_REASON") -> None:
        """
        Adds a ban to a channel.
        
        Args:
            ban_id (int | str): A user id to ban.
            reason (str): The reason for the ban.
        """
        async with aiohttp.ClientSession() as session:
            if isinstance(ban_id, str):
                ban_id = await self.get_id(ban_id)
                
            url = f'{self.config["twitch"]["api_uri"]}/moderation/bans?broadcaster_id={str(self.id)}&moderator_id={str(self.id)}'
            data = {
                "data": {
                    'user_id': ban_id,
                    'reason': reason
                }
            }
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}',
                'Content-Type': 'application/json'
            }
            async with session.post(url, headers=headers, json=data) as resp:
                response_data = await resp.json()
                return response_data
            
    async def unban(self, ban_id: int | str) -> None:
        """
        Removes a ban or a timeout from a channel.
        
        Args:
            ban_id (int | str): A user id to unban.
        """
        if isinstance(ban_id, str):
            ban_id = await self.get_id(ban_id)
            
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/moderation/bans?broadcaster_id={str(self.id)}&moderator_id={str(self.id)}&user_id={ban_id}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.delete(url, headers=headers) as resp:
                pass
    
    async def announce(self, message: str, color: str = "primary") -> None:
        """
        Sends an announcement in a channel.
        
        Args:
            message (str): The message to send.
            color (str): The color of the message.
        """
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/chat/announcements?broadcaster_id={str(self.id)}&moderator_id={str(self.id)}'
            colors = ["blue", "green", "orange", "purple", "primary"]
            data = {
                'message': message,
                'color': color if color in colors else "primary"
            }
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}',
                'Content-Type': 'application/json'
            }
            async with session.post(url, headers=headers, json=data) as resp:
                response_data = await resp.json()
                return response_data
            
    async def whisper(self, to_user_id: int | str, message: str) -> None:
        """
        Sends a whisper message to the specified user.
        
        **Rate Limits:**
            You may whisper to a maximum of 40 unique recipients per day. Within the per day limit, you may whisper a maximum of 3 whispers per second and a maximum of 100 whispers per minute.
        
        Args:
            to_user_id (int | str): The user id of the user to send the whisper to.
            message (str): The message to send.
        """
        if isinstance(to_user_id, str):
            to_user_id = await self.get_id(to_user_id)
            
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/whispers?from_user_id={str(self.id)}&to_id={str(to_user_id)}'
            data = {
                'from_user_id': self.id,
                'to_user_id': to_user_id,
                'message': message
            }
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}',
                'Content-Type': 'application/json'
            }
            async with session.post(url, headers=headers, json=data) as resp:
                response_data = await resp.json()
                return response_data
            
    # ==================================================================================================================
    # Checks
    # ==================================================================================================================
    
    def is_live(self) -> bool:
        """
        Checks if a channel is live.
        
        Returns:
            bool: True if the channel is live, False if the channel is offline.
        """
        return self.is_live
    
    def is_follower(self, username: str) -> bool:
        """
        Checks if a user is a follower of a channel.
        
        Args:
            username (str): The name of the user.
            
        Returns:
            bool: True if the user is a follower, False if the user is not a follower.
        """
        return username.lower() in self.followers
    
    def is_sub(self, username: str) -> bool:
        """
        Checks if a user is a subscriber of a channel.
        
        Args:
            username (str): The name of the user.
            
        Returns:
            bool: True if the user is a subscriber, False if the user is not a subscriber.
        """
        return username.lower() in self.subscribers
    
    def is_vip(self, username: str) -> bool:
        """
        Checks if a user is a VIP of a channel.
        
        Args:
            username (str): The name of the user.
            
        Returns:
            bool: True if the user is a VIP, False if the user is not a VIP.
        """
        return username.lower() in self.vips
    
    def is_mod(self, username: str) -> bool:
        """
        Checks if a user is a moderator of a channel.
        
        Args:
            username (str): The name of the user.
            
        Returns:
            bool: True if the user is a moderator, False if the user is not a moderator.
        """
        return username.lower() in self.moderators
    
    def is_banned(self, username: str) -> bool:
        """
        Checks if a user is banned from a channel.
        
        Args:
            username (str): The name of the user.
            
        Returns:
            bool: True if the user is banned, False if the user is not banned.
        """
        return username.lower() in self.banned
