import asyncio
import logging
import os

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
        for v in valky:
            self.logger.info(v)
        if os.path.exists(config_path):
            self._cfg = ValkyrieConfig(config_path, self.logger, self.debug)
        else:
            raise ConfigError(f"Configuration file not found: {config_path}")
        self.config = self._cfg.get_config()
        self.tw_bot = TwitchBot(self.config, self.logger)
        self.dc_bot = DiscordBot(self.config, self.tw_bot, self.logger)
    
    def run(self):
        # Create an asyncio event loop
        loop = asyncio.get_event_loop()
        
        # Start the Discord bot and the Twitch bot concurrently
        self.dc_bot.setup()
        loop.create_task(self.dc_bot.client.start(self.dc_bot.token))
        loop.create_task(self.tw_bot.run())
        
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            # Cleanup and close the event loop
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()


if __name__ == "__main__":
    _debug = False
    
    start_arg = ValkyrieOptions([('config_file', 'str', 'Configuration File Path and filename', 'settings.json')])
    parsed_options = start_arg.parse()
    
    _config_file = parsed_options['config_file']

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
        r"======================================================================================================="
    ]

    try:
        VB = ValkyrieBot(_config_file, _debug)
        VB.run()

    except Exception as exc:
        logging.error(exc)
    