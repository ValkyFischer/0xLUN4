#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky

--------

About:
    This script provides a class for Luna API requests. The Luna API is used to translate text and answer questions.

"""
import requests


class Luna:
    """
    A class for Luna API requests. The Luna API is used to translate text and answer questions.
    
    Args:
        logger (ValkyrieLogger): The logger.
        config (dict): The configuration dictionary.
    """
    def __init__(self, logger, config):
        self.config = config
        self.logger = logger
        
        self.luna_origin = f'https://{self.config["luna"]["host"]}:{self.config["luna"]["port"]}'
        self.luna_version = f'v{self.config["luna"]["version"]}'
        self.luna_rest_url = f'{self.luna_origin}/rest/{self.luna_version}'
        
        self.response = {"msg": "API Error!", "Return": False, "ReturnCode": 3}
    
    def _pingUrl(self) -> str:
        """
        Returns the ping url.
        
        Returns:
            str: The ping url.
        """
        return f'{self.luna_rest_url}/ping'
    
    def _translateUrl(self) -> str:
        """
        Returns the translation url.
        
        Returns:
            str: The translation url.
        """
        return f'{self.luna_rest_url}/translate'
    
    def _askUrl(self) -> str:
        """
        Returns the ask url.
        
        Returns:
            str: The ask url.
        """
        return f'{self.luna_rest_url}/ask'
    
    async def lunaPing(self) -> dict:
        """
        Pings the Luna API.
        
        Returns:
            dict: A dictionary of information.
        """
        response = self.response
        
        try:
            x = requests.post(url=self._pingUrl(), json={})
            ping = int(x.elapsed.microseconds / 1000)
            
            response = {
                "msg": "Command successfull",
                "Return": True,
                "ReturnCode": 1,
                "data": ping
            }
            self.logger.info(f'Luna Ping | Latency: {ping}ms')
            
        except requests.RequestException as e:
            self.logger.error(f'Failed to make the request: {str(e)}')
        
        return response
    
    async def lunaTranslate(self, text: str, lang: str = "en") -> dict:
        """
        Translates text using the Luna API.
        
        Args:
            text (str): The text to translate.
            lang (str): The language to translate to. Defaults to `en`.
            
        Returns:
            dict: A dictionary of information.
        """
        response = self.response
        request_data = {
            "message": text,
            "language": lang
        }
        headers = {"Content-Type": "application/json"}
        self.logger.info(f'Luna Translate | Text: {text}')
        try:
            x = requests.request(method="POST", url=self._translateUrl(), json=request_data, headers=headers)
            data = x.json()
            
            response = {
                "msg": "Command successfull",
                "Return": True,
                "ReturnCode": 1,
                "data": data['Data']
            }
            self.logger.info(f'Luna Translate | Answer: {data["Data"]}')
            
        except requests.RequestException as e:
            self.logger.error(f'Failed to make the request: {str(e)}')
        
        return response
    
    async def lunaAsk(self, text: str) -> dict:
        """
        Asks Luna a question using the Luna API.
        
        Args:
            text (str): The question to ask.
            
        Returns:
            dict: A dictionary of information.
        """
        response = self.response
        request_data = {
            "message": text
        }
        headers = {"Content-Type": "application/json"}
        try:
            x = requests.request(method="POST", url=self._askUrl(), json=request_data, headers=headers)
            data = x.json()
            
            response = {
                "msg": "Command successfull",
                "Return": True,
                "ReturnCode": 1,
                "data": data['Data']
            }
            self.logger.info(f'Luna Ask | Question: {text}')
            self.logger.info(f'Luna Ask | Answer: {data["Data"]}')
            
        except requests.RequestException as e:
            self.logger.error(f'Failed to make the request: {str(e)}')
        
        return response
