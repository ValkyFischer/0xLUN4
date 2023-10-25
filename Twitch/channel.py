import logging
import aiohttp

from ValkyrieUtils.Tools import ValkyrieTools


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
        self.stream = stream
        
    async def setup(self, user_id: int):
        """
        Sets up the channel by getting the emotes, followers, subscribers, VIPs, moderators, and stream information.
        
        Args:
            user_id (int): The user id of the channel.
        """
        # get the emotes of the channel
        emotes = await self.get_emotes(user_id)
        for emote in emotes:
            if emote.get('name') not in self.emotes:
                self.emotes.append(emote.get('name'))
        self.logger.info(f'Twitch Emotes | {len(self.emotes)}')
        
        # get the followers of the channel
        followers = await self.get_followers(user_id)
        self.follower_count = await self.get_followers(user_id, True)
        for follower in followers:
            if follower.get('user_name') not in self.followers:
                self.followers.append(follower.get('user_name')) if follower.get('user_name').lower() != self.name.lower() else None
        self.logger.info(f'Twitch Followers | {self.follower_count}')
        
        # get the subscribers of the channel
        subscribers = await self.get_subscribers(user_id)
        self.subscriber_count = await self.get_subscribers(user_id, True)
        for subscriber in subscribers:
            if subscriber.get('user_name') not in self.subscribers:
                self.subscribers.append(subscriber.get('user_name')) if subscriber.get('user_name').lower() != self.name.lower() else None
        self.logger.info(f'Twitch Subscribers | {self.subscriber_count}')
        
        # get the VIPs of the channel
        vips = await self.get_vips(user_id)
        for vip in vips:
            if vip.get('user_name') not in self.vips:
                self.vips.append(vip.get('user_name')) if vip.get('user_name').lower() != self.name.lower() else None
        self.logger.info(f'Twitch VIPs | {len(self.vips)}')
        
        # get the moderators of the channel
        moderators = await self.get_moderators(user_id)
        for moderator in moderators:
            if moderator.get('user_name') not in self.moderators:
                self.moderators.append(moderator.get('user_name')) if moderator.get('user_name').lower() != self.name.lower() else None
        self.logger.info(f'Twitch Moderators | {len(self.moderators)}')
        
        # get the stream information of the channel
        info = await self.get_info(await self.get_id(self.name))
        
        self.stream.title = info.get('title')
        self.stream.game.name = info.get('game_name')
        self.stream.game.id = info.get('game_id')
        self.stream.tags = info.get('tags')
        self.stream.language = info.get('broadcaster_language')
        self.stream.classification = info.get('content_classification_labels')
        
        self.logger.info(f'Twitch Stream | Title: {self.stream.title} | Game: {self.stream.game.name} | Language: {self.stream.language}')

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
    
    async def get_info(self, user_id: int) -> dict:
        """
        Gets the information of a channel.
        
        Args:
            user_id (int): The user id of the channel.
            
        Returns:
            dict: A dictionary of information.
        """
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/channels?broadcaster_id={str(user_id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data.get('data')[0]
    
    async def set_info(self, user_id: int = None, title: str = None, game_name: str = None, language: str = None, tags: list = None) -> bool:
        """
        Sets the information of a channel.
        
        Args:
            user_id (int): The user id of the channel. Defaults to `self.id`
            title (str): The title of the stream. Defaults to `self.stream.title`
            game_name (str): The name of the game used to get the game id. Defaults to `self.stream.game.id`
            language (str): The language of the stream. Defaults to `self.stream.language`
            tags (list): A list of tags. Defaults to `self.stream.tags`
            
        Returns:
            bool: True if the information was set, False if the information was not set.
        """
        
        if user_id is None:
            user_id = self.id
        else:
            self.id = user_id
            
        if title is None:
            title = self.stream.title
        else:
            self.stream.title = title
            
        if game_name is None:
            game_id = self.stream.game.id
        else:
            game_id = await self.stream.game.get_id(game_name, self.config['twitch']['client_id'], self.config['twitch']['bot_token'])
            if ValkyrieTools.isInteger(game_id):
                game_id = int(game_id)
                self.stream.game.id = game_id
            else:
                self.logger.error(f'Failed to get game id: {game_id}')
                return False
            
        if language is None:
            language = self.stream.language
        else:
            language = language.lower()
            self.stream.language = language
            
        if tags is None:
            tags = self.stream.tags
        else:
            self.stream.tags = tags
        
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/channels?broadcaster_id={str(user_id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            data = {
                'title': title,
                'game_id': game_id,
                'broadcaster_language': language,
                'tags': tags
            }
            async with session.patch(url, headers=headers, data=data) as resp:
                if resp.status == 204:
                    return True
                return False
            
    async def get_status(self, user_id: int = None) -> bool:
        """
        Gets the status of a channel.
        
        Args:
            user_id (int): The user id of the channel.
            
        Returns:
            bool: True if the channel is live, False if the channel is offline.
        """
        if user_id is None:
            user_id = self.id
            
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/streams?user_id={str(user_id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                if response_data.get('data'):
                    return True
                return False
            
    async def get_emotes(self, user_id: int) -> list:
        """
        Gets the emotes of a channel.
        
        Args:
            user_id (int): The user id of the channel.
            
        Returns:
            list: A list of emotes.
        """
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/chat/emotes?broadcaster_id={str(user_id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data.get('data')
    
    async def get_followers(self, user_id: int, total: bool = False) -> list:
        """
        Gets the followers of a channel.
        
        Args:
            user_id (int): The user id of the channel.
            total (bool): True if the total number of followers should be returned, False if the list of followers
                should be returned.
            
        Returns:
            list: A list of followers.
        """
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/channels/followers?broadcaster_id={str(user_id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                if total:
                    return response_data.get('total')
                return response_data.get('data')
    
    async def get_subscribers(self, user_id: int, total: bool = False) -> list:
        """
        Gets the subscribers of a channel.
        
        Args:
            user_id (int): The user id of the channel.
            total (bool): True if the total number of subscribers should be returned, False if the list of subscribers
                should be returned.
            
        Returns:
            list: A list of subscribers.
        """
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/subscriptions?broadcaster_id={str(user_id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                if total:
                    return response_data.get('total')
                return response_data.get('data')
    
    async def get_vips(self, user_id: int) -> list:
        """
        Gets the VIPs of a channel.
        
        Args:
            user_id (int): The user id of the channel.
            
        Returns:
            list: A list of VIPs.
        """
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/channels/vips?broadcaster_id={str(user_id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data.get('data')
    
    async def get_moderators(self, user_id: int) -> list:
        """
        Gets the moderators of a channel.
        
        Args:
            user_id (int): The user id of the channel.
            
        Returns:
            list: A list of moderators.
        """
        async with aiohttp.ClientSession() as session:
            url = f'{self.config["twitch"]["api_uri"]}/moderation/moderators?broadcaster_id={str(user_id)}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data.get('data')
