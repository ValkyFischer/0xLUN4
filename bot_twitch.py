import logging

import aiohttp
import twitchio
from twitchio.ext import commands


class TwitchBot(commands.Bot):
    """
    A Twitch bot that can be used to check if a channel is live or not. It utilizes the Twitch API to check if a channel
    is live or not. It also has a few commands that can be used in chat.
    
    Args:
        client_id (str): The client id of the Twitch application.
        bot_token (str): The bot token of the Twitch application.
        channels (list[str, str]): A list of channels to join and check.
        prefix (str): The prefix to use for commands. Defaults to '!'.
    """
    def __init__(self, client_id: str, bot_token: str, channels: list[str, str], prefix: str = '!', logger: logging.Logger = None):
        self.logger = logger if logger else logging.getLogger(__name__)
        self.client_id = client_id
        self.bot_token = bot_token
        self.channels = channels
        self.prefix = prefix
        super().__init__(token = self.bot_token, prefix = self.prefix, initial_channels = self.channels)

    async def event_ready(self):
        print(f'Twitch Bot logged in as {self.nick}')
        print(f'Twitch Bot user id is {self.user_id}')
        print(f'Twitch Bot joined {len(self.channels)} Channels')
        for channel in self.channels:
            await self.check_live(channel.strip('#'))

    async def check_live(self, user_name):
        user_id = await self.get_user_id(user_name)
        is_live = await self.is_user_live(user_id)
        print(f'Check if channel is live | {user_name}: {is_live}')

    async def get_user_id(self, username):
        async with aiohttp.ClientSession() as session:
            url = f'https://api.twitch.tv/helix/users?login={username}'
            headers = {'Client-ID': self.client_id, 'Authorization': f'Bearer {self.bot_token}'}
            async with session.get(url, headers=headers) as resp:
                response_data = await resp.json()
                return response_data.get('data')[0].get('id')
            
    async def is_user_live(self, user_id):
        async with aiohttp.ClientSession() as session:
            url = f'https://api.twitch.tv/helix/streams?user_id={user_id}'
            headers = {'Client-ID': self.client_id, 'Authorization': f'Bearer {self.bot_token}'}
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
        print('Twitch Command | ping')
        await ctx.send(f'Pong!')

    @commands.command()
    async def discord(self, ctx: commands.Context):
        print('Twitch Command | discord')
        await ctx.send(f'Want to ask something specific? Want to know more about Valky? Join the Discord community! | https://discord.gg/vky')

