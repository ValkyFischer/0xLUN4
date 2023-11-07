#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky

--------

About:
    This script is the main bot script that will run the Discord bot and the Twitch bot concurrently. This script will
    also handle the configuration file and the logger. The configuration file will be used to configure the bots. The
    logger will be used to log messages to a log file.

--------

Example:
    To use this bot, you can interact with it in your Discord server or Twitch chat. Here are some example commands:
    
    1. Check the bot's latency:
       >> /ping
       This command will show the bot's latency in milliseconds.
    
    2. Get the Discord invite link:
       >> /discord
       This command will provide you with the Discord invite link to join the community.

"""

import asyncio
import logging
import os

from ValkyrieUtils.Config import ValkyrieConfig
from ValkyrieUtils.Logger import ValkyrieLogger
from ValkyrieUtils.Options import ValkyrieOptions
from ValkyrieUtils.Exceptions import *

from bot_twitch import TwitchBot
from bot_discord import DiscordBot
from bot_valkyrie import ValkyrieBot

from Modules.tasks import TaskQueue
from bot_web import WebServer


class Valkyrie:
    """
    The main bot class that will run the Discord bot and the Twitch bot concurrently. This class will also handle the
    configuration file and the logger. The configuration file will be used to configure the bots. The logger will be
    used to log messages to a log file.
    
    Args:
        config_path (str): The path to the configuration file.
        debug (bool): True if debug mode is enabled, False if debug mode is disabled.
    """
    def __init__(self, config_path: str, debug: bool):
        self.debug = debug
        self.logger = ValkyrieLogger('info', 'logs/logger.log', 'ValkyrieBot', True, self.debug)
        for v in valky:
            self.logger.info(v)
        if os.path.exists(config_path):
            self._cfg = ValkyrieConfig(config_path, self.logger, self.debug)
        else:
            raise ConfigError(f"Configuration file not found: {config_path}")
        self.config = self._cfg.get_config()
        self.task_queue = TaskQueue(self.config, self.logger)
        self.tw_bot = TwitchBot(self.config, self.logger, self.task_queue)
        self.dc_bot = DiscordBot(self.config, self.logger, self.task_queue)
        self.vk_bot = ValkyrieBot(self.tw_bot, self.dc_bot, self.config, self.logger, self.task_queue)
        self.web = WebServer(self.tw_bot, self.dc_bot, self.vk_bot, self.logger, self.config, valky)
    
    def run(self):
        """
        Runs the Valkyrie Bot web server and gives an asyncio event loop to its run function. The web server allows to
        run a Discord bot and the Twitch bot concurrently in one loop.
        
        The event loop will run until the user presses CTRL+C.
        """
        loop = asyncio.get_event_loop()
        loop.create_task(self.web.run(loop))
        
        try:
            # run until CTRL+C
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            # cleanup
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()


if __name__ == "__main__":
    
    start_arg = ValkyrieOptions([
        ('config_file', 'str', 'Configuration File Path and filename', 'settings.json'),
        ('debug', 'str', 'Enable Debug Mode', 'False')
    ])
    parsed_options = start_arg.parse()
    
    _config_file = parsed_options['config_file']
    _debug = True if parsed_options['debug'].lower() == 'true' else False

    valky = [
        r"=======================================================================================================",
        r"                                                                                                       ",
        r"          (`-.     ('-.              .-. .-')                      _ .-') _     ('-.        (`-.       ",
        r"        _(OO  )_  ( OO ).-.          \  ( OO )                    ( (  OO) )  _(  OO)     _(OO  )_     ",
        r"    ,--(_/   ,. \ / . --. / ,--.     ,--. ,--.   ,--.   ,--.       \     .'_ (,------.,--(_/   ,. \    ",
        r"    \   \   /(__/ | \-.  \  |  |.-') |  .'   /    \  `.'  /        ,`'--..._) |  .---'\   \   /(__/    ",
        r"     \   \ /   /.-'-'  |  | |  | OO )|      /,  .-')     /         |  |  \  ' |  |     \   \ /   /     ",
        r"      \   '   /, \| |_.'  | |  |`-' ||     ' _)(OO  \   /          |  |   ' |(|  '--.   \   '   /,     ",
        r"       \     /__) |  .-.  |(|  '---.'|  .   \   |   /  /\_         |  |   / : |  .--'    \     /__)    ",
        r"        \   /     |  | |  | |      | |  |\   \  `-./  /.__)        |  '--'  / |  `---.    \   /        ",
        r"         `-'      `--' `--' `------' `--' '--'    `--'             `-------'  `------'     `-'         ",
        r"                                                                                                       ",
        r"==v=================================================================================================v=="
    ]

    try:
        VB = Valkyrie(_config_file, _debug)
        VB.run()

    except Exception as exc:
        logging.error(exc)
    