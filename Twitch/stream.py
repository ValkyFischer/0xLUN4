#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky

--------

About:
    This script provides the functionality to set and get the information of a Twitch stream and game.

"""
import aiohttp

from ValkyrieUtils.Logger import ValkyrieLogger
from ValkyrieUtils.Tools import ValkyrieTools


class Stream:
    """
    A class storing Twitch stream information.
    
    Properties:
        - title (str): The title of the stream.
        - game (Game): The game being played on the stream.
        - tags (list): The tags of the stream.
        - language (str): The language of the stream.
        - classification (list): The classification of the stream.
    
    Args:
        config (dict): The configuration dictionary.
        logger (ValkyrieLogger): The logger.
    """
    def __init__(self, config: dict, logger: ValkyrieLogger):
        self.config = config
        self.logger = logger
        
        self.title = ''
        self.game = Game(self.config, self.logger)
        self.tags = []
        self.language = ''
        self.classification = []
    
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
    
    async def set_info(self, user_id: int, title: str = None, game_name: str = None, language: str = None, tags: list = None) -> bool:
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
        
        if title is None:
            title = self.title
        else:
            self.title = title
            
        if game_name is None:
            game_id = self.game.id
        else:
            game_id = await self.game.get_id(game_name)
            if ValkyrieTools.isInteger(game_id):
                game_id = int(game_id)
                self.game.id = game_id
            else:
                self.logger.error(f'Failed to get game id: {game_id}')
                return False
            
        if language is None:
            language = self.language
        else:
            language = language.lower()
            self.language = language
            
        if tags is None:
            tags = self.tags
        else:
            self.tags = tags
        
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


class Game:
    """
    A class storing Twitch stream game information.
    
    Properties:
        - name (str): The name of the game.
        - id (int): The id of the game.
        
    Args:
        config (dict): The configuration dictionary.
        logger (ValkyrieLogger): The logger.
    """
    def __init__(self, config: dict, logger: ValkyrieLogger):
        self.config = config
        self.logger = logger
        
        self.name = ''
        self.id = 0
    
    async def get_id(self, name: str) -> int:
        """
        Gets the game id from the game name.
        
        Args:
            name (str): The name of the game.
            
        Returns:
            int: The id of the game.
        """
        url = f'{self.config["twitch"]["api_uri"]}/games?name={name}'
        headers = {
            'Client-ID': self.config['twitch']['client_id'],
            'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                return data['data'][0]['id']
