
import datetime
import logging
import aiohttp
from twitchio.ext import commands


class TwitchBot(commands.Bot):
    """
    A Twitch bot that can be used to check if a channel is live or not. It utilizes the Twitch API to check if a channel
    is live or not. It also has a few commands that can be used in chat.
    
    Args:
        config (dict): The configuration file.
        logger (logging.Logger): The logger.
    """
    def __init__(self, config: dict, logger: logging.Logger):
        self.logger = logger
        self.config = config
        prefix = self.config['twitch']['prefix']
        bot_token = self.config['twitch']['bot_token']
        channels = [f"#{x}" for x in self.config['twitch']['channels']]
        super().__init__(token = bot_token, prefix = prefix, initial_channels = channels)

    async def event_ready(self):
        self.logger.info(f'Twitch Bot logged in as {self.nick}')
        self.logger.info(f'Twitch Bot user id is {self.user_id}')
        self.logger.info(f'Twitch Bot joined {len(self.config["twitch"]["channels"])} Channels')
        self.logger.info('=' * 103)

    async def check_live(self, user_name):
        user_id = await self.get_user_id(user_name)
        is_live = await self.is_user_live(user_id)
        old_status = self.config['twitch']['channels'].get(user_name)
        if old_status is None:
            self.config['twitch']['channels'][user_name] = is_live
        elif old_status != is_live:
            if is_live:
                self.logger.info(f'Channel went live | {user_name}')
            else:
                self.logger.info(f'Channel went offline | {user_name}')
            self.config['twitch']['channels'][user_name] = is_live
        return is_live

    async def get_user_id(self, username):
        async with aiohttp.ClientSession() as session:
            url = f'https://api.twitch.tv/helix/users?login={username}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data.get('data')[0].get('id')
            
    async def is_user_live(self, user_id):
        async with aiohttp.ClientSession() as session:
            url = f'https://api.twitch.tv/helix/streams?user_id={user_id}'
            headers = {
                'Client-ID': self.config['twitch']['client_id'],
                'Authorization': f'Bearer {self.config["twitch"]["bot_token"]}'
            }
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                if response_data.get('data'):
                    return True
                return False

    # ==================================================================================================================
    # Commands
    # ==================================================================================================================

    @commands.command()
    async def ping(self, ctx: commands.Context):
        self.logger.info(f'Twitch Command | ping | {ctx.author.name}')
        msg_time = datetime.datetime.utcnow()
        await ctx.send(f'[PING] Pong! | {round((msg_time - ctx.message.timestamp).total_seconds()) * 100}ms')

    @commands.command()
    async def discord(self, ctx: commands.Context):
        self.logger.info(f'Twitch Command | discord | {ctx.author.name}')
        await ctx.send(f'[DISCORD] Want to ask something specific? Want to know more about Valky? Join the Discord community! | https://discord.gg/vky')
        
    @commands.command()
    async def exval(self, ctx: commands.Context):
        self.logger.info(f'Twitch Command | exval | {ctx.author.name}')
        await ctx.send(f'[EXVAL] Want to know more about ExVal Limited? Check out the official website of ExVal Ltd. | https://exv.al/en')
