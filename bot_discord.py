
import asyncio
import discord
from discord import app_commands


class DiscordBot:
    def __init__(self, config, twitch_bot, logger):
        self.logger = logger
        self.config = config
        self.token = self.config['discord']['bot_token']
        self.guild_id = self.config['discord']['guild_id']
        self.activity = discord.Activity(name="Tests", type=5)
        self.intents = discord.Intents.all()
        self.client = discord.Client(intents=self.intents, activity=self.activity)
        self.tree = app_commands.CommandTree(self.client)
        self.guild = discord.Object(id=self.guild_id)
        
        self.twitch_bot = twitch_bot
        
        self.ch_admin = None
        self.ch_cmd = None
        self.ch_stream = None
    
    async def check_live_loop(self):
        await asyncio.sleep(10)
        while True:
            for channel in self.config['twitch']['channels'].keys():
                is_live = await self.twitch_bot.check_live(channel)
                self.logger.info(f'{channel} is live: {is_live}')
                if is_live:
                    await self.send_notification(f'{channel} is live')
                    self.config['discord']['channels'][channel] = True
                else:
                    self.config['discord']['channels'][channel] = False
                    
            await asyncio.sleep(60)
    
    async def send_notification(self, message):
        if self.ch_admin:
            await self.ch_admin.send(message)

    def setup(self):

        @self.client.event
        async def on_ready():
            await self.tree.sync(guild=self.guild)
            self.logger.info(f'Discord Bot logged in as {self.client.user}')
            self.logger.info(f'Discord Bot user id is {self.client.user.id}')
            self.logger.info(f'Discord Bot joined {len(self.client.guilds)} Discords')
            self.ch_admin = self.client.get_channel(int(self.config['discord']['channels'].get("admin")))
            self.ch_cmd = self.client.get_channel(int(self.config['discord']['channels'].get("commands")))
            self.ch_stream = self.client.get_channel(int(self.config['discord']['channels'].get("stream")))
            self.client.loop.create_task(self.check_live_loop())
            self.logger.info(f'Discord Bot loaded all tasks')
            self.logger.info('=' * 103)
        
        # ==============================================================================================================
        # Commands
        # ==============================================================================================================
        
        @self.tree.command(name="ping", description="Test Bot Latency", guild=self.guild)
        async def dc_ping(interaction):
            self.logger.info(f'Discord Command | ping | {interaction.user.name}')
            await interaction.response.send_message(f"[PING] Pong! | {round(self.client.latency * 1000)}ms")
        
        @self.tree.command(name="discord", description="Discord Invite Link", guild=self.guild)
        async def dc_discord(interaction):
            self.logger.info(f'Discord Command | discord | {interaction.user.name}')
            await interaction.response.send_message(f"[DISCORD] You can use the following link to invite your friends. |  https://discord.gg/vky")
        
        @self.tree.command(name="twitch", description="Twitch Channel Link", guild=self.guild)
        async def dc_twitch(interaction):
            self.logger.info(f'Discord Command | twitch | {interaction.user.name}')
            await interaction.response.send_message(f"[TWITCH] Want to watch Valky live? Follow on Twitch and dont miss the next stream. | https://twitch.tv/v_lky")
        
        @self.tree.command(name="exval", description="ExVal Limited Link", guild=self.guild)
        async def dc_exval(interaction):
            self.logger.info(f'Discord Command | exval | {interaction.user.name}')
            await interaction.response.send_message(f"[EXVAL] Want to know more about ExVal Limited? Check out the official website of ExVal Ltd. | https://exv.al/en")
            