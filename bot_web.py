#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky
"""

import time
from threading import Thread

import requests
from waitress import serve
from flask import Flask, request, render_template, session, redirect, flash

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
        self.luna_time = 0
        self.luna_ping = 0
        self.luna_interval = self.config['luna']['interval']
        
        self.tw_bot = twitch_b
        self.dc_bot = discord_b
        self.vk_bot = valky_b
        
        self.app = Flask(__name__, static_folder='Web/data', template_folder='Web/views')
        self.app.config['SECRET_KEY'] = self.config['web']['token']
        self.app.config['SESSION_COOKIE_SECURE'] = True
        
        self.loop = None
        
        self.setup()
        
    def setup(self):
        """
        Sets up the web server.
        """
        # index
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/<lang>', 'index', self.index)
        self.app.add_url_rule('/<lang>/', 'index', self.index)
        # logs
        self.app.add_url_rule('/<lang>/logs', 'logs', self.logs)
        self.app.add_url_rule('/<lang>/logs/', 'logs', self.logs)
        # functions
        self.app.add_url_rule('/login', 'login', self.login, methods=['POST'])
        self.app.add_url_rule('/logout', 'logout', self.logout)
        self.app.add_url_rule('/start/<bot>', 'start_bot', self.start_bot)
        # valky
        self.app.add_url_rule('/<lang>/valky', 'valky', self.valky_bot)
        self.app.add_url_rule('/<lang>/valky/', 'valky', self.valky_bot)
        self.app.add_url_rule('/<lang>/valky/status', 'valky', self.valky_bot)
        self.app.add_url_rule('/<lang>/valky/status/', 'valky', self.valky_bot)
        self.app.add_url_rule('/<lang>/valky/settings', 'valky_settings', self.valky_settings)
        self.app.add_url_rule('/<lang>/valky/settings/', 'valky_settings', self.valky_settings)
        self.app.add_url_rule('/<lang>/valky/luna', 'valky_luna', self.valky_luna)
        self.app.add_url_rule('/<lang>/valky/luna/', 'valky_luna', self.valky_luna)
        self.app.add_url_rule('/<lang>/valky/tasks', 'valky_tasks', self.valky_tasks)
        self.app.add_url_rule('/<lang>/valky/tasks/', 'valky_tasks', self.valky_tasks)
    
    # ========================================================================================
    # Valkyrie Bot - Views
    # ========================================================================================
    
    # Index
    def index(self, lang='en'):
        """
        The index page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return render_template('index.html', stringtable=ST[lang])
        
        logs = self.getLogs()
        latest_5 = logs[-5:]
        
        if self.luna_time + self.luna_interval < time.time():
            try:
                x = requests.post(url = f"{self.luna.luna_rest_url}/ping", json = {})
                self.luna_ping = int(x.elapsed.microseconds / 1000)
                data = x.json()
                self.luna_time = data['Timestamp']
                server_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['Timestamp']))
                self.logger.info(f'Luna Ping | Latency: {self.luna_ping}ms')
                
            except requests.RequestException as e:
                self.logger.error(f'Failed to make the request: {str(e)}')
                self.luna_ping = 0
                server_time = 'N/A'
        else:
            server_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.luna_time))
        
        return render_template(
            template_name_or_list='index.html',
            stringtable=ST[lang],
            vk_status=self.vk_bot.ready,
            dc_status=self.dc_bot.loaded,
            tw_status=self.tw_bot.loaded,
            logs=latest_5,
            l4_status='OFFLINE' if self.luna_ping == 0 else 'ONLINE',
            ping=self.luna_ping,
            server_time=server_time
        )
    
    def logs(self, lang='en'):
        """
        The logs page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        logs = self.getLogs()
        return render_template(
            template_name_or_list='logs.html',
            stringtable=ST[lang],
            logs=logs
        )
    
    # Valky
    async def valky_bot(self, lang='en'):
        """
        The Valkyrie bot page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        tasks, finished = self.getTasks()
        tasks_5 = tasks[-5:]
        finished_5 = finished[-5:]
        
        return render_template(
            template_name_or_list='valky.html',
            stringtable=ST[lang],
            vk_status=self.vk_bot.ready,
            tasks=tasks_5,
            finished=finished_5,
        )
    
    async def valky_settings(self, lang='en'):
        """
        The Valkyrie bot settings page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        return render_template(
            template_name_or_list='valky/settings.html',
            stringtable=ST[lang],
            vk_status=self.vk_bot.ready,
            config=self.config
        )
    
    async def valky_luna(self, lang='en'):
        """
        The Valkyrie bot Luna page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        return render_template(
            template_name_or_list='valky/luna.html',
            stringtable=ST[lang],
            vk_status=self.vk_bot.ready,
            config=self.config
        )
    
    async def valky_tasks(self, lang='en'):
        """
        The Valkyrie bot tasks page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        tasks, finished = self.getTasks()
        
        return render_template(
            template_name_or_list='valky/tasks.html',
            stringtable=ST[lang],
            vk_status=self.vk_bot.ready,
            tasks=tasks,
            finished=finished
        )
    
    # ========================================================================================
    # Valkyrie Bot - Functions
    # ========================================================================================
    
    def login(self):
        """
        The login page.
        """
        input_login = request.form.get('login')
        input_password = request.form.get('pass')
        if input_login == self.config['web']['user'] and input_password == self.config['web']['pass']:
            session['loggedin'] = True
            flash('You were successfully logged in', 'info')
            return redirect('/')
        
        return redirect('https://valky.xyz/')
    
    def logout(self):
        """
        The logout page.
        """
        session.pop('loggedin', None)
        flash('You were successfully logged out', 'info')
        return redirect('https://valky.xyz/')
    
    def start_bot(self, bot):
        """
        Starts a bot.
        """
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
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
            return redirect('https://valky.xyz/')
        
        thread = Thread(target=meth)
        thread.start()
        
        flash(f'Started {name} Bot', 'info')
        return redirect('/')
    
    # ========================================================================================
    # Valkyrie Bot - Helpers
    # ========================================================================================
    
    def start_vk_bot(self):
        """
        Starts the Valkyrie bot.
        """
        self.loop.create_task(self.vk_bot.run())
        
    def start_dc_bot(self):
        """
        Starts the Discord bot.
        """
        self.dc_bot.setup()
        self.loop.create_task(self.dc_bot.client.start(self.dc_bot.token))
        
    def start_tw_bot(self):
        """
        Starts the Twitch bot.
        """
        self.loop.create_task(self.tw_bot.run())
    
    def getLogs(self):
        """
        Returns the logs.
        """
        logs = []
        path = self.logger.PATH
        start_string = self.valky[-1] + "'"
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
    
    def getTasks(self):
        tasks_raw = self.vk_bot.task_queue.tasks
        tasks = []
        for task in tasks_raw:
            task.data['id'] = task.id
            task.data['action'] = task.action
            tasks.append(task.data)
        
        finished_raw = self.vk_bot.task_queue.finished_tasks
        finished = []
        for task in finished_raw:
            task.data['id'] = task.id
            task.data['action'] = task.action
            finished.append(task.data)
        
        return tasks, finished
    
    # ========================================================================================
    # Valkyrie Bot - Serve
    # ========================================================================================
    
    def run(self, loop):
        """
        Runs the web server using waitress.
        """
        self.loop = loop
        self.logger.info(f'Web | Starting web server on port {self.config["web"]["port"]}...')
        serve(self.app, host=self.config['web']['host'], port=self.config['web']['port'])
