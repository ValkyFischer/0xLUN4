import logging
import multiprocessing
import os
import time

from ValkyrieUtils.Config import ValkyrieConfig
from ValkyrieUtils.Logger import ValkyrieLogger
from ValkyrieUtils.Options import ValkyrieOptions
from ValkyrieUtils.Exceptions import *

from bot_twitch import TwitchBot
from bot_discord import DiscordBot


class ValkyrieBot:
    def __init__(self, config_path, debug):
        self.debug = debug
        self.logger = ValkyrieLogger('info', 'logger.log', 'ValkyrieBot', True, self.debug)
        if os.path.exists(config_path):
            self._cfg = ValkyrieConfig(config_path, self.logger, self.debug)
        else:
            raise ConfigError(f"Configuration file not found: {config_path}")
        self.config = self._cfg.get_config()
        
    # Twitch bot setup
    def run_twitch(self):
        # https://twitchtokengenerator.com/
        client_id = self.config['twitch']['client_id']
        bot_token = self.config['twitch']['bot_token']
        channels = self.config['twitch']['channels']
        prefix = self.config['twitch']['prefix']
        
        tw_bot = TwitchBot(client_id, bot_token, channels, prefix)
        tw_bot.run()
    
    # Discord bot setup
    def run_discord(self):
        bot_token = self.config['discord']['bot_token']
        guild_id = self.config['discord']['guild_id']
    
        dc_bot = DiscordBot(bot_token, guild_id)
        dc_bot.run()
    
    def run(self):
        # Twitch bot
        twitch_process = multiprocessing.Process(target = self.run_twitch)
        discord_process = multiprocessing.Process(target = self.run_discord)
        twitch_process.daemon = True
        discord_process.daemon = True
        twitch_process.start()
        discord_process.start()
        twitch_process.join()
        discord_process.join()


if __name__ == "__main__":
    _debug = False
    
    start_arg = ValkyrieOptions([('config_file', 'str', 'Configuration File Path and filename', 'settings.json')])
    parsed_options = start_arg.parse()
    
    _config_file = parsed_options['config_file']

    try:
        APE = ValkyrieBot(_config_file, _debug)
        APE.run()

    except Exception as exc:
        logging.error(exc)
    