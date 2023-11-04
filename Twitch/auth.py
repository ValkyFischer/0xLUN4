#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky

--------

About:
    This script provides the functionality to authorize the bot to use the Twitch API.

"""
import json
import http.server
import os
import socketserver
import webbrowser
import requests

from ValkyrieUtils.Logger import ValkyrieLogger
from ValkyrieUtils.Config import ValkyrieConfig

CODE = None


class NullOutput:
    def write(self, s):
        pass


class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """
    A class which handles the OAuth callback.
    """
    
    def log_message(self, format, *args):
        """
        Disables the logging of the web server.
        """
        pass
    
    def do_GET(self):
        """
        Handles the GET request. This method will get the OAuth code from the URL.
        """
        global CODE
        try:
            CODE = self.path.split('?code=')[1].split("&scope")[0]
        except IndexError:
            pass
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'OAuth code received. You can now close this page.')
        

class Auth:
    """
    A class which handles the authorization of the Twitch bot.
    """
    def __init__(self, config: dict, logger: ValkyrieLogger):
        self.config = config
        self.logger = logger
        
    def authorize(self, client_id: str, client_secret: str, redirect_uri: str, scopes: list, kind: str = "user") -> str:
        """
        Authorizes the bot to use the Twitch API.
        
        Args:
            client_id (str): The client id of the bot.
            client_secret (str): The client secret of the bot.
            redirect_uri (str): The redirect uri of the bot.
            scopes (list): The scopes of the bot.
            kind (str): The kind of authorization. Can be either "user" or "bot".
        """
        refresh = False
        if kind == "user":
            self.logger.info('Authorizing Twitch Account')
            path = 'Twitch/data/bot/user.vcf'
        elif kind == "bot":
            self.logger.info('Authorizing Twitch Bot')
            path = 'Twitch/data/bot/bot.vcf'
        else:
            raise Exception(f'Invalid kind: {kind}')
        
        if os.path.exists(path):
            cfg = ValkyrieConfig(path, self.logger, False).get_config()
            if cfg.get('token') is not None:
                self.config['twitch'][kind]['token'] = cfg.get('token')
                self.config['twitch'][kind]['refresh_token'] = cfg.get('refresh_token')
                self.config['twitch'][kind]['token_expires'] = cfg.get('token_expires')
                refresh = True
        
        if refresh:
            data = self._refresh_token(client_id, client_secret, self.config['twitch'][kind]['refresh_token'])
        else:
            code = self._get_auth_code(client_id, redirect_uri, scopes)
            data = self._get_auth_token(client_id, client_secret, code, redirect_uri)
        
        self.config['twitch'][kind]['token'] = data.get('access_token')
        self.config['twitch'][kind]['refresh_token'] = data.get('refresh_token')
        self.config['twitch'][kind]['token_expires'] = data.get('expires_in')
        
        cfg = ValkyrieConfig(path, self.logger, False)
        cfg.save(self.config['twitch'][kind], path)
        
        return self.config['twitch'][kind]['token']
        
    def _get_auth_code(self, client_id: str, redirect_uri: str, scopes: list) -> str:
        """
        Gets the OAuth code for the bot. This code will be used to get the OAuth token for the bot.
        
        Args:
            client_id (str): The client id of the bot.
            redirect_uri (str): The redirect uri of the bot.
            scopes (list): The scopes of the bot.
            
        Returns:
            str: The OAuth code for the bot.
        """
        url = f'https://id.twitch.tv/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={"+".join(scopes)}'
        # Create a local web server to listen for the response
        server_address = ('', 8000)  # You can choose a different port if needed
        httpd = socketserver.TCPServer(server_address, OAuthCallbackHandler)
        
        try:
            # Open the authorization URL in the browser for the user to log in and grant authorization
            webbrowser.open(url)
            # Start the web server to listen for the response
            httpd.handle_request()
        
        finally:
            # Close the web server when done
            httpd.server_close()

            if CODE is not None:
                self.logger.info(f'Twitch OAuth code received')
                return CODE
            else:
                raise Exception('Failed to get OAuth code')
        
    def _get_auth_token(self, client_id: str, client_secret: str, code: str, redirect_uri: str) -> dict:
        """
        Gets the OAuth token for the bot.
        
        Args:
            client_id (str): The client id of the bot.
            client_secret (str): The client secret of the bot.
            code (str): The OAuth code for the bot.
            redirect_uri (str): The redirect uri of the bot.
            
        Returns:
            str: The OAuth dict for the bot.
        """
        url = f'https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={redirect_uri}'
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            self.logger.info(f'Twitch OAuth token received')
            return response_data
        
    def _refresh_token(self, client_id: str, client_secret: str, refresh_token: str) -> dict:
        """
        Refreshes the OAuth token for the bot.
        
        Args:
            client_id (str): The client id of the bot.
            client_secret (str): The client secret of the bot.
            refresh_token (str): The refresh token for the bot.
            
        Returns:
            str: The OAuth dict for the bot.
        """
        url = f'https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=refresh_token&refresh_token={refresh_token}'
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            self.logger.info(f'Twitch OAuth token refreshed')
            return response_data
        else:
            raise Exception(f'Failed to refresh OAuth token: {response.text}')
