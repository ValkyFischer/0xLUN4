import logging

import discord
from discord import app_commands

class DiscordBot:
    def __init__(self, token, guild_id):
        self.token = token
        self.guild_id = guild_id
        self.activity = discord.Activity(name="Tests", type=5)
        self.intents = discord.Intents.all()
        self.client = discord.Client(intents=self.intents, activity=self.activity)
        self.tree = app_commands.CommandTree(self.client)
        self.guild = discord.Object(id=self.guild_id)

    def run(self):
        @self.tree.command(name="ping", description="Test Latency", guild=self.guild)
        async def ping(interaction):
            print(f'Discord Command | ping')
            await interaction.response.send_message(f"Pong! {round(self.client.latency * 1000)}ms")

        @self.client.event
        async def on_ready():
            await self.tree.sync(guild=self.guild)
            print(f'Discord Bot logged in as {self.client.user}')
            print(f'Discord Bot user id is {self.client.user.id}')
            print(f'Discord Bot joined {len(self.client.guilds)} Discords')
            
        self.client.run(self.token, log_handler=None)
