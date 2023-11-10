#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky
"""

import time
from binascii import hexlify
from threading import Thread

import requests
from waitress import serve
from flask import Flask, request, render_template, session, redirect, flash
from Web.stringtable import ST

from ValkyrieUtils.Tools import ValkyrieTools
from Modules.tasks import Task
from Modules.luna import Luna


class WebServer:
    """
    A class for web management of all bots.
    """
    def __init__(self, twitch_b, discord_b, valky_b, logger, config, valky):
        self.cfg = config[0]
        self.config = config[1]
        self.logger = logger
        self.valky = valky
        self.build = hexlify(self.config['version'].replace('.', '').encode()).decode('utf-8').replace('2d', ':')
        self.build_v = self.build.split(':')[1]
        
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
        # valky
        self.app.add_url_rule('/<lang>/valky', 'valky', self.valky_bot)
        self.app.add_url_rule('/<lang>/valky/', 'valky', self.valky_bot)
        # twitch
        self.app.add_url_rule('/<lang>/twitch', 'twitch', self.twitch_bot)
        self.app.add_url_rule('/<lang>/twitch/', 'twitch', self.twitch_bot)
        self.app.add_url_rule('/<lang>/twitch', 'twitch_post', self.twitch_bot_post, methods=['POST'])
        self.app.add_url_rule('/<lang>/twitch/', 'twitch_post', self.twitch_bot_post, methods=['POST'])
        # tasks
        self.app.add_url_rule('/<lang>/tasks', 'valky_tasks', self.valky_tasks)
        self.app.add_url_rule('/<lang>/tasks/', 'valky_tasks', self.valky_tasks)
        self.app.add_url_rule('/<lang>/tasks/new', 'valky_tasks_new', self.valky_tasks_new)
        self.app.add_url_rule('/<lang>/tasks/new/', 'valky_tasks_new', self.valky_tasks_new)
        self.app.add_url_rule('/<lang>/tasks/new', 'valky_tasks_post', self.valky_tasks_post, methods=['POST'])
        self.app.add_url_rule('/<lang>/tasks/new/', 'valky_tasks_post', self.valky_tasks_post, methods=['POST'])
        self.app.add_url_rule('/<lang>/tasks/<task_id>/<action>', 'valky_tasks_action', self.valky_tasks_action)
        # settings
        self.app.add_url_rule('/<lang>/settings/web', 'valky_settings', self.valky_settings)
        self.app.add_url_rule('/<lang>/settings/web/', 'valky_settings', self.valky_settings)
        self.app.add_url_rule('/<lang>/settings/web', 'valky_settings_post', self.settings_post, methods=['POST'])
        self.app.add_url_rule('/<lang>/settings/web/', 'valky_settings_post', self.settings_post, methods=['POST'])
        self.app.add_url_rule('/<lang>/settings/luna', 'luna_settings', self.luna_settings)
        self.app.add_url_rule('/<lang>/settings/luna/', 'luna_settings', self.luna_settings)
        self.app.add_url_rule('/<lang>/settings/luna', 'luna_settings_post', self.settings_post, methods=['POST'])
        self.app.add_url_rule('/<lang>/settings/luna/', 'luna_settings_post', self.settings_post, methods=['POST'])
        self.app.add_url_rule('/<lang>/settings/twitch', 'twitch_settings', self.twitch_settings)
        self.app.add_url_rule('/<lang>/settings/twitch/', 'twitch_settings', self.twitch_settings)
        self.app.add_url_rule('/<lang>/settings/twitch', 'twitch_settings_post', self.settings_post, methods=['POST'])
        self.app.add_url_rule('/<lang>/settings/twitch/', 'twitch_settings_post', self.settings_post, methods=['POST'])
        self.app.add_url_rule('/<lang>/settings/discord', 'discord_settings', self.discord_settings)
        self.app.add_url_rule('/<lang>/settings/discord/', 'discord_settings', self.discord_settings)
        self.app.add_url_rule('/<lang>/settings/discord', 'discord_settings_post', self.settings_post, methods=['POST'])
        self.app.add_url_rule('/<lang>/settings/discord/', 'discord_settings_post', self.settings_post, methods=['POST'])
        self.app.add_url_rule('/<lang>/settings/scopes', 'twitch_settings_scope', self.twitch_settings_scope)
        self.app.add_url_rule('/<lang>/settings/scopes/', 'twitch_settings_scope', self.twitch_settings_scope)
        self.app.add_url_rule('/<lang>/settings/scopes', 'twitch_settings_scope_post', self.settings_post, methods=['POST'])
        self.app.add_url_rule('/<lang>/settings/scopes/', 'twitch_settings_scope_post', self.settings_post, methods=['POST'])

        # functions
        self.app.add_url_rule('/login', 'login', self.login, methods=['POST'])
        self.app.add_url_rule('/logout', 'logout', self.logout)
        self.app.add_url_rule('/start/<bot>', 'start_bot', self.start_bot)
    
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
        
        logs = self.get_logs()
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
        
        if self.vk_bot is not None:
            if self.vk_bot.ready:
                vk_status = 'ONLINE'
            elif self.vk_bot.running:
                vk_status = 'STARTED'
            else:
                vk_status = 'OFFLINE'
        else:
            vk_status = 'UNKNOWN'
        
        if self.dc_bot is not None:
            if self.dc_bot.loaded:
                dc_status = 'ONLINE'
            elif self.dc_bot.running:
                dc_status = 'STARTED'
            else:
                dc_status = 'OFFLINE'
        else:
            dc_status = 'UNKNOWN'
        
        if self.tw_bot is not None:
            if self.tw_bot.loaded:
                tw_status = 'ONLINE'
            elif self.tw_bot.running:
                tw_status = 'STARTED'
            else:
                tw_status = 'OFFLINE'
        else:
            tw_status = 'UNKNOWN'
            
        return render_template(
            template_name_or_list='index.html',
            stringtable=ST[lang],
            vk_status=vk_status,
            dc_status=dc_status,
            tw_status=tw_status,
            logs=latest_5,
            l4_status='OFFLINE' if self.luna_ping == 0 else 'ONLINE',
            ping=self.luna_ping,
            build=self.build,
            build_v=self.build_v,
            vk_start_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.vk_bot.start_time)),
            dc_start_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.dc_bot.start_time)),
            tw_start_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.tw_bot.start_time)),
            l4_server_time=server_time,
        )
    
    def logs(self, lang='en'):
        """
        The logs page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        logs = self.get_logs()
        return render_template(
            template_name_or_list='logs.html',
            stringtable=ST[lang],
            logs=logs,
            build=self.build,
            build_v=self.build_v
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

        if self.vk_bot is not None:
            if self.vk_bot.ready:
                vk_status = 'ONLINE'
            elif self.vk_bot.running:
                vk_status = 'STARTED'
            else:
                vk_status = 'OFFLINE'
        else:
            vk_status = 'UNKNOWN'
            
        tasks, finished, deleted, errors = self.get_tasks()
        tasks_5 = tasks[-5:]
        finished_5 = finished[-5:]
        
        return render_template(
            template_name_or_list='valky.html',
            stringtable=ST[lang],
            vk_status=vk_status,
            tasks=tasks_5,
            finished=finished_5,
            build=self.build,
            build_v=self.build_v,
        )
    
    async def valky_tasks(self, lang='en'):
        """
        The tasks queue page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        tasks, finished, deleted, errors = self.get_tasks()
        
        return render_template(
            template_name_or_list='valky/tasks.html',
            stringtable=ST[lang],
            vk_status=self.vk_bot.ready,
            tasks=tasks,
            finished=finished,
            deleted=deleted,
            errors=errors,
            build=self.build,
            build_v=self.build_v
        )
    
    async def valky_tasks_new(self, lang='en'):
        """
        The tasks creation page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        return render_template(
            template_name_or_list='valky/tasks_new.html',
            stringtable=ST[lang],
            vk_status=self.vk_bot.ready,
            actions=self.vk_bot.task_queue.__globals__(),
            build=self.build,
            build_v=self.build_v
        )
        
    # Twitch
    async def twitch_bot(self, lang = 'en'):
        """
        The Twitch bot page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        if self.tw_bot is not None:
            if self.tw_bot.loaded:
                tw_status = 'ONLINE'
            elif self.tw_bot.running:
                tw_status = 'STARTED'
            else:
                tw_status = 'OFFLINE'
        else:
            tw_status = 'UNKNOWN'
        
        return render_template(
            template_name_or_list = 'twitch.html',
            stringtable = ST[lang],
            tw_status = tw_status,
            build = self.build,
            build_v = self.build_v,
            is_live = self.tw_bot.channel.is_live,
            stream_title = self.tw_bot.stream.title,
            stream_game = self.tw_bot.stream.game.name,
            follower_count = self.tw_bot.channel.follower_count,
            subscriber_count = self.tw_bot.channel.subscriber_count,
            vip_count = len(self.tw_bot.channel.vips),
            mod_count = len(self.tw_bot.channel.moderators),
            emote_count = len(self.tw_bot.channel.emotes),
            emotes = self.tw_bot.channel.emotes_raw,
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
            config=self.config,
            build=self.build,
            build_v=self.build_v
        )
    
    async def luna_settings(self, lang= 'en'):
        """
        The Luna API settings page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        return render_template(
            template_name_or_list='valky/luna.html',
            stringtable=ST[lang],
            vk_status=self.vk_bot.ready,
            config=self.config,
            build=self.build,
            build_v=self.build_v
        )
    
    async def twitch_settings(self, lang='en'):
        """
        The Twitch bot settings page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        return render_template(
            template_name_or_list='twitch/settings.html',
            stringtable=ST[lang],
            vk_status=self.vk_bot.ready,
            config=self.config,
            build=self.build,
            build_v=self.build_v
        )
    
    async def twitch_settings_scope(self, lang='en'):
        """
        The Twitch bot scope settings page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        return render_template(
            template_name_or_list='twitch/scopes.html',
            stringtable=ST[lang],
            vk_status=self.vk_bot.ready,
            config=self.config,
            build=self.build,
            build_v=self.build_v
        )
    
    # Discord
    async def discord_settings(self, lang='en'):
        """
        The Discord bot settings page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        return render_template(
            template_name_or_list='discord/settings.html',
            stringtable=ST[lang],
            vk_status=self.vk_bot.ready,
            config=self.config,
            build=self.build,
            build_v=self.build_v
        )
    
    async def valky_tasks_post(self, lang='en'):
        """
        The Valkyrie bot tasks page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        data = request.form.to_dict()
        if data['submit'] == 'add':
            task_action = data['task_action']
            task_instant = True if data['task_exec'] == '1' else False
            task_data = {
                'user_name': data['task_name'],
                'reward_name': data['task_reward'],
                'reward_cost': data['task_cost'],
                'user_input': data['task_input'],
            }
            time_frame = int(data['task_time']) if data['task_time'] != '' else None
            role_assign = data['task_role'] if data['task_role'] != '' else None
            
            if self.vk_bot.task_queue.TASK_TW_TIMEOUT == task_action:
                if time_frame is None:
                    flash(f'Time frame is required for this task: {task_action}', category='error')
                    return redirect(f'/{lang}/tasks')
                if data['task_input'] is None or data['task_input'] == '':
                    flash(f'Input is required for this task: {task_action}', category='error')
                    return redirect(f'/{lang}/tasks')
            
            if self.vk_bot.task_queue.TASK_DC_ADD_ROLE == task_action:
                if role_assign is None:
                    flash(f'Role is required for this task: {task_action}', category='error')
                    return redirect(f'/{lang}/tasks')
                if data['task_input'] is None or data['task_input'] == '':
                    flash(f'Input is required for this task: {task_action}', category='error')
                    return redirect(f'/{lang}/tasks')
            
            if self.vk_bot.task_queue.TASK_TW_ADD_MODERATOR == task_action:
                if data['task_input'] is None or data['task_input'] == '':
                    flash(f'Input is required for this task: {task_action}', category='error')
                    return redirect(f'/{lang}/tasks')
            
            if self.vk_bot.task_queue.TASK_TW_ADD_VIP == task_action:
                if data['task_input'] is None or data['task_input'] == '':
                    flash(f'Input is required for this task: {task_action}', category='error')
                    return redirect(f'/{lang}/tasks')
            
            task = Task(task_action, task_data, task_instant, time_frame, role_assign)
            self.vk_bot.task_queue.add_task(task)
            flash(f'Task "{task}" added', category='info')
            return redirect(f'/{lang}/tasks')
        
        else:
            flash('Unknown action', category='error')
            return redirect(f'/{lang}/tasks')
    
    async def valky_tasks_action(self, task_id, action, lang='en'):
        """
        The Valkyrie bot tasks action page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        if not ValkyrieTools.isInteger(task_id):
            return redirect('https://valky.xyz/')
        task_id = int(task_id)
        
        if action not in ['delete', 'start', 'end', 'queue']:
            self.logger.error(f'Unknown action: {action}')
            flash('Unknown action', category='error')
            return redirect(f'/{lang}/tasks')
        
        if action == 'delete':
            task = self.vk_bot.task_queue.get_task_by_id(task_id)
            self.vk_bot.task_queue.remove_task(task)
            flash(f'Task "{task.action}" ({task.id}) deleted', category='info')
            return redirect(f'/{lang}/tasks')
        
        elif action == 'start':
            task = self.vk_bot.task_queue.get_task_by_id(task_id)
            self.vk_bot.task_queue.add_task(task, True)
            flash('Task restarted', category='info')
            return redirect(f'/{lang}/tasks')
        
        elif action == 'end':
            task = self.vk_bot.task_queue.get_task_by_id(task_id)
            self.vk_bot.task_queue.end_task(task)
            flash('Task ended', category='info')
            return redirect(f'/{lang}/tasks')
        
        elif action == 'queue':
            task = self.vk_bot.task_queue.get_task_by_id(task_id)
            self.vk_bot.task_queue.add_task(task)
            flash('Task queued', category='info')
            return redirect(f'/{lang}/tasks')
    
    async def twitch_bot_post(self, lang='en'):
        """
        The Twitch bot page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')
        
        data = request.form.to_dict()
        if data['submit'] == 'stream':
            if data['stream_title'] is None or data['stream_title'] == '':
                flash('Stream title is required', category='error')
                return redirect(f'/{lang}/twitch')
            
            await self.tw_bot.stream.set_info(
                user_id = self.tw_bot.channel.id,
                title = data['stream_title'],
                game_name = data['stream_game']
            )
            self.logger.info(f'Twitch | Stream information updated | {data["stream_title"]} | {data["stream_game"]}')
            flash('Stream information updated', category='info')
            return redirect(f'/{lang}/twitch')
        
        else:
            self.logger.error(f'Unknown action: {data["submit"]}')
            flash('Unknown action', category='error')
            return redirect(f'/{lang}/twitch')
    
    async def settings_post(self, lang='en'):
        """
        The Valkyrie bot settings page.
        """
        if lang not in ['en', 'de', 'ru', 'vk']:
            lang = 'en'
        
        if 'loggedin' not in session:
            return redirect('https://valky.xyz/')

        data = request.form.to_dict()
        if data['submit'] == 'web':
            self.config['web']['host'] = data['web_host']
            self.config['web']['port'] = int(data['web_port'])
            self.config['interval'] = int(data['update_interval'])
            self.config['web']['token'] = data['web_token']
            self.config['web']['user'] = data['web_user']
            self.config['web']['pass'] = data['web_pass']
            self.save_cfg()
            
            self.logger.info(f'Web | Settings updated | {data}')
            flash('Settings updated', category='info')
            return redirect(f'/{lang}/settings/web')
        
        elif data['submit'] == 'luna':
            self.config['luna']['host'] = data['luna_host']
            self.config['luna']['port'] = int(data['luna_port'])
            self.config['luna']['version'] = int(data['luna_version'])
            self.config['luna']['interval'] = int(data['luna_interval'])
            self.config['luna']['token'] = data['luna_token']
            self.save_cfg()
            
            self.logger.info(f'Web | Settings updated | {data}')
            flash('Settings updated', category='info')
            return redirect(f'/{lang}/settings/luna')
        
        elif data['submit'] == 'twitch':
            self.config['twitch']['channel'] = data['tw_channel']
            self.config['twitch']['prefix'] = data['tw_prefix']
            self.config['twitch']['api_uri'] = data['tw_api']
            self.config['twitch']['redirect_uri'] = data['tw_redr']
            self.config['twitch']['user']['client_id'] = data['user_id']
            self.config['twitch']['user']['client_secret'] = data['user_secret']
            self.config['twitch']['bot']['client_id'] = data['bot_id']
            self.config['twitch']['bot']['client_secret'] = data['bot_secret']
            self.save_cfg()
            
            self.logger.info(f'Web | Settings updated | {data}')
            flash('Settings updated', category='info')
            return redirect(f'/{lang}/settings/twitch')
        
        elif data['submit'] == 'discord':
            self.config['discord']['bot_token'] = data['dc_token']
            self.config['discord']['guild_id'] = data['dc_guild']
            self.config['discord']['channels']['admin'] = data['dc_admin']
            self.config['discord']['channels']['commands'] = data['dc_cmd']
            self.config['discord']['channels']['stream'] = data['dc_announce']
            self.save_cfg()
            
            self.logger.info(f'Web | Settings updated | {data}')
            flash('Settings updated', category='info')
            return redirect(f'/{lang}/settings/discord')
        
        elif data['submit'] == 'scopes':
            for scope, status in self.config['twitch']['scopes'].items():
                self.config['twitch']['scopes'][scope] = True if scope in data else False
            self.save_cfg()
            
            self.logger.info(f'Web | Settings updated | {data}')
            flash('Settings updated', category='info')
            return redirect(f'/{lang}/settings/scopes')
        
        else:
            self.logger.error(f'Unknown action: {data["submit"]}')
            flash('Unknown action', category='error')
            return redirect('https://valky.xyz/')
    
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
            flash('You were successfully logged in', category='info')
            return redirect('/')
        
        return redirect('https://valky.xyz/')
    
    def logout(self):
        """
        The logout page.
        """
        session.pop('loggedin', None)
        flash('You were successfully logged out', category='info')
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
        
        flash(f'Started {name} Bot', category='info')
        return redirect('/')
    
    # ========================================================================================
    # Valkyrie Bot - Helpers
    # ========================================================================================
    
    def start_vk_bot(self):
        """
        Starts the Valkyrie bot.
        """
        self.vk_bot.start_time = time.time()
        self.vk_bot.running = True
        self.loop.create_task(self.vk_bot.run())
        self.loop.create_task(self.vk_bot.run_fast())
        
    def start_dc_bot(self):
        """
        Starts the Discord bot.
        """
        self.dc_bot.start_time = time.time()
        self.dc_bot.running = True
        self.dc_bot.setup()
        self.loop.create_task(self.dc_bot.client.start(self.dc_bot.token))
        
    def start_tw_bot(self):
        """
        Starts the Twitch bot.
        """
        self.tw_bot.start_time = time.time()
        self.tw_bot.running = True
        self.loop.create_task(self.tw_bot.run())
    
    def get_logs(self):
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
    
    def get_tasks(self):
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
        
        deleted_raw = self.vk_bot.task_queue.deleted_tasks
        deleted = []
        for task in deleted_raw:
            task.data['id'] = task.id
            task.data['action'] = task.action
            deleted.append(task.data)
        
        errors_raw = self.vk_bot.task_queue.errors
        errors = []
        for task in errors_raw:
            task.data['id'] = task.id
            task.data['action'] = task.action
            errors.append(task.data)
        
        return tasks, finished, deleted, errors
    
    def save_cfg(self):
        """
        Saves the configuration file.
        
        Note:
            This function will pop the tokens and refresh tokens from the configuration file before saving it. After
            saving the configuration file, the tokens and refresh tokens will be added back to the configuration
            dictionary.
        """
        pop_utoken = self.config['twitch']['user'].pop('token')
        pop_urefresh = self.config['twitch']['user'].pop('refresh_token')
        pop_uexpire = self.config['twitch']['user'].pop('token_expires')
        pop_btoken = self.config['twitch']['bot'].pop('token')
        pop_brefresh = self.config['twitch']['bot'].pop('refresh_token')
        pop_bexpire = self.config['twitch']['bot'].pop('token_expires')
        
        self.cfg.save(self.config)
        
        self.config['twitch']['user']['token'] = pop_utoken
        self.config['twitch']['user']['refresh_token'] = pop_urefresh
        self.config['twitch']['user']['token_expires'] = pop_uexpire
        self.config['twitch']['bot']['token'] = pop_btoken
        self.config['twitch']['bot']['refresh_token'] = pop_brefresh
        self.config['twitch']['bot']['token_expires'] = pop_bexpire
    
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
