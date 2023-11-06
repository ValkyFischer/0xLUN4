#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky
"""
import asyncio
import logging
import time
from threading import Thread

import requests
from waitress import serve
from flask import Flask, request, jsonify, render_template, session, redirect, flash

from Web.stringtable import ST
from Modules.luna import Luna


class WebServer:
    """
    A class for web management of all bots.
    """
    def __init__(self, twitch_b, discord_b, valky_b, logger, config, valky):
        self.config = config
        self.logger = logger
        self.valky = valky
        self.luna = Luna(self.logger, self.config)
        
        self.tw_bot = twitch_b
        self.dc_bot = discord_b
        self.vk_bot = valky_b
        
        self.app = Flask(__name__, static_folder='Web/data', template_folder='Web/views')
        self.app.config['SECRET_KEY'] = self.config['web']['token']
        
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/<lang>', 'index', self.index)
        self.app.add_url_rule('/<lang>/', 'index', self.index)
        self.app.add_url_rule('/<lang>/logs', 'logs', self.logs)
        self.app.add_url_rule('/<lang>/logs/', 'logs', self.logs)
        self.app.add_url_rule('/login', 'login', self.login, methods=['POST'])
        self.app.add_url_rule('/logout', 'logout', self.logout)
        self.app.add_url_rule('/start/<bot>', 'start_bot', self.start_bot)
        
    def index(self, lang='en'):
        """
        The index page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' in session:
            logs = self.getLogs()
            latest_5 = logs[-5:]

            try:
                x = requests.post(url = f"{self.luna.luna_rest_url}/ping", json = {})
                ping = int(x.elapsed.microseconds / 1000)
                data = x.json()
                server_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['Timestamp']))
            except requests.RequestException as e:
                self.logger.error(f'Failed to make the request: {str(e)}')
                ping = 0
                server_time = 'N/A'
                
            l4_status = 'OFFLINE' if ping == 0 else 'ONLINE'
            
            return render_template(
                template_name_or_list='index.html',
                stringtable=ST[lang],
                vk_status=self.vk_bot.ready,
                dc_status=self.dc_bot.loaded,
                tw_status=False,
                logs=latest_5,
                l4_status=l4_status,
                ping=ping,
                server_time=server_time
            )
        return render_template('index.html', stringtable=ST[lang])
    
    def logs(self, lang='en'):
        """
        The logs page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' in session:
            logs = self.getLogs()
            return render_template(
                template_name_or_list='logs.html',
                stringtable=ST[lang],
                logs=logs
            )
        return redirect('/')
    
    def getLogs(self):
        """
        Returns the logs.
        """
        logs = []
        path = self.logger.PATH
        start_string = self.valky[-1]+"'"
        with open(path, 'r') as f:
            last_part = f.read().split(start_string)[-1]
        for l in last_part.split('\n'):
            if l == '':
                continue
            log_data = l[:-1].replace("b'", '').replace('b"', '').split(' | ', 5)
            
            if log_data[5] != self.valky[0]:
                logs.append({
                    'time': log_data[0],
                    'level': log_data[1],
                    'file': log_data[2],
                    'line': log_data[3],
                    'method': log_data[4],
                    'message': log_data[5]
                })
        return logs
    
    def login(self):
        """
        The login page.
        """
        input_login = request.form.get('login')
        input_password = request.form.get('pass')
        if input_login == self.config['web']['user'] and input_password == self.config['web']['pass']:
            session['loggedin'] = True
            flash('You were successfully logged in', 'info')
        else:
            flash('Invalid username/password combination', 'error')
            session.pop('loggedin', None)
        
        return redirect('/')
    
    def logout(self):
        """
        The logout page.
        """
        session.pop('loggedin', None)
        flash('You were successfully logged out', 'info')
        return redirect('/')
    
    def start_bot(self, bot):
        """
        Starts a bot.
        """
        if bot == 'vk':
            meth = self.start_vk_bot
            name = 'Valkyrie'
        elif bot == 'dc':
            meth = self.start_dc_bot
            name = 'Discord'
        elif bot == 'tw':
            meth = self.start_tw_bot
            name = 'Twitch'
        else:
            return redirect('/')
        
        thread = Thread(target=meth)
        thread.start()
        
        flash(f'Started {name} Bot', 'info')
        return redirect('/')
    
    def start_vk_bot(self):
        """
        Starts the Valkyrie bot.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.vk_bot.run())
        loop.run_forever()
        
    def start_dc_bot(self):
        """
        Starts the Discord bot.
        """
        # self.dc_bot.setup()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.dc_bot.client.start(self.dc_bot.token))
        loop.run_forever()
        
    def start_tw_bot(self):
        """
        Starts the Twitch bot.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.tw_bot.run())
        loop.run_forever()
    
    def run(self):
        """
        Runs the web server using waitress.
        """
        self.logger.info(f'Web | Starting web server on port {self.config["web"]["port"]}...')
        serve(self.app, host=self.config['web']['host'], port=self.config['web']['port'])
