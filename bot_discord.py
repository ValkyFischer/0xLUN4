#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Oct 23, 2023
@author: v_lky

--------

About:
    This script is a Discord bot that can be used to send notifications to a Discord server. The bot uses the Discord
    API to send notifications and to use slash commands. The bot also uses the Twitch API to check if a channel is live
    or not. The bot will send a notification to the Discord server when a channel goes live or offline.

--------

Example:
    To use this Discord bot, you can interact with it in your Discord server. Here are some example commands:
    
    1. Check the bot's latency:
       >> /ping
       This command will show the bot's latency in milliseconds.
            
    2. Get the Discord invite link:
       >> /discord
       This command will provide you with the Discord invite link to join the community.
            
    3. Get the Twitch channel link:
       >> /twitch
       This command will provide you with a link to the Twitch channel.
            
    4. Get the ExVal Limited link:
       >> /exval
       This command will provide you with a link to the official website of ExVal Ltd.
    
"""

import datetime
import os

import discord

from discord import app_commands, ui

from ValkyrieUtils.Logger import ValkyrieLogger

from Modules.luna import Luna
from Modules.tasks import TaskQueue

LUNA: Luna = None


class DiscordBot:
    """
    A Discord bot that can be used to send notifications to a Discord server. The bot uses the Discord API to send
    notifications and to use slash commands. The bot also uses the Twitch API to check if a channel is live or not.
    
    Args:
        config (dict): The configuration dictionary.
        logger (ValkyrieLogger): The logger.
        task_queue (TaskQueue): The queue.
    """
    def __init__(self, config: dict, logger: ValkyrieLogger, task_queue: TaskQueue):
        self.loaded = False
        self.logger = logger
        self.config = config
        self.task_queue = task_queue
        self.token = self.config['discord']['bot_token']
        self.guild_id = self.config['discord']['guild_id']
        self.activity = discord.Activity(name="Artificial Tasks", type=4, state='Working on 𝗔𝗿𝘁𝗶𝗳𝗶𝗰𝗶𝗮𝗹 𝗧𝗮𝘀𝗸𝘀')
        self.intents = discord.Intents.all()
        self.client = discord.Client(intents=self.intents, activity=self.activity)
        self.tree = app_commands.CommandTree(self.client)
        self.guild = discord.Object(id=self.guild_id)
        
        self.ch_admin = None
        self.ch_cmd = None
        self.ch_stream = None
        
        self.start_time = 0
        
        global LUNA
        LUNA = Luna(self.logger, self.config)
        if not os.path.exists("Discord/data/tickets.txt"):
            self.write_ticket(0)
    
    @staticmethod
    def write_ticket(i):
        with open("Discord/data/tickets.txt", "w") as f:
            f.write(str(i))
    
    @staticmethod
    def read_ticket():
        with open("Discord/data/tickets.txt", "r") as f:
            return int(f.read())
    
    async def send_log(self, message: str):
        """
        Sends a message to the admin channel. The message will be formatted as a simple message with a [LOG] prefix.
        
        Args:
            message (str): The message to send.
        """
        if self.ch_admin:
            await self.ch_admin.send(f"[LOG] {message}")
    
    async def send_notification(self, channel: str):
        """
        Sends a message to the stream channel. The message will be formatted as an embed message.
        
        Args:
            channel (str): The channel that went live.
        """
        await self.send_log(f'{channel} went live')
        # TODO: Proper embedded message
        #       await self.ch_stream.send(message)
    
    async def assign_role(self, user_id: int | str):
        """
        Assigns a role to a user.
        
        Args:
            user_id (int | str): The user to assign the role to.
        """
        for user in self.client.users:
            if user.name == user_id or user.id == user_id:
                guild = await self.client.fetch_guild(self.guild_id)
                user = await guild.fetch_member(user.id)
                for rwd in self.config['twitch']['rewards']:
                    if rwd['task'] == "discord_role":
                        role = discord.utils.get(guild.roles, name=rwd['role'])
                        await user.add_roles(role)
                        return

    def setup(self):
        """
        Sets up the Discord bot. This method will be called before the bot starts, adds all slash commands
        to the bot, and will set up the on_ready event.
        
        The following commands will be added:
            - ping
            - discord
            - twitch
            - exval
        """
        @self.client.event
        async def on_ready():
            """
            This event is called once when the bot goes online.
            """
            await self.tree.sync(guild=self.guild)
            
            self.logger.info(f'Discord Bot logged in as {self.client.user}')
            self.logger.info(f'Discord Bot user id is {self.client.user.id}')
            self.logger.info(f'Discord Bot joined {len(self.client.guilds)} Discords')
            self.ch_admin = self.client.get_channel(int(self.config['discord']['channels'].get("admin")))
            self.ch_cmd = self.client.get_channel(int(self.config['discord']['channels'].get("commands")))
            self.ch_stream = self.client.get_channel(int(self.config['discord']['channels'].get("stream")))
            self.logger.info(f'Discord Members | {len(self.client.users)}')
            
            self.loaded = True
        
        # ==============================================================================================================
        # Commands
        # ==============================================================================================================
        
        @self.tree.command(name="ping", description="Test Bot Latency", guild=self.guild)
        async def dc_ping(interaction):
            """
            This command will show the bot's latency in milliseconds.
            
            Args:
                interaction (any): The interaction object.
            """
            self.logger.info(f'Discord Command | ping | {interaction.user.name}')
            await interaction.response.send_message(f"[PING] Pong! | {round(self.client.latency * 1000)}ms")
            await self.send_log(f'{interaction.user.name} pinged the bot')
        
        @self.tree.command(name="discord", description="Discord Invite Link", guild=self.guild)
        async def dc_discord(interaction):
            """
            This command will provide you with the Discord invite link to join the community.
            
            Args:
                interaction (any): The interaction object.
            """
            self.logger.info(f'Discord Command | discord | {interaction.user.name}')
            await interaction.response.send_message(f"[DISCORD] You can use the following link to invite your friends. |  https://discord.gg/vky")
            await self.send_log(f'{interaction.user.name} requested the Discord invite link')
        
        @self.tree.command(name="twitch", description="Twitch Channel Link", guild=self.guild)
        async def dc_twitch(interaction):
            """
            This command will provide you with a link to the Twitch channel.
            
            Args:
                interaction (any): The interaction object.
            """
            self.logger.info(f'Discord Command | twitch | {interaction.user.name}')
            await interaction.response.send_message(f"[TWITCH] Want to watch Valky live? Follow on Twitch and dont miss the next stream. | https://twitch.tv/v_lky")
            await self.send_log(f'{interaction.user.name} requested the Twitch channel link')
        
        @self.tree.command(name="exval", description="ExVal Limited Link", guild=self.guild)
        async def dc_exval(interaction):
            """
            This command will provide you with a link to the official website of ExVal Ltd.
            
            Args:
                interaction (any): The interaction object.
            """
            self.logger.info(f'Discord Command | exval | {interaction.user.name}')
            await interaction.response.send_message(f"[EXVAL] Want to know more about ExVal Limited? Check out the official website of ExVal Ltd. | https://exv.al/en")
            await self.send_log(f'{interaction.user.name} requested the ExVal Limited link')
        
        @self.tree.command(name="translate", description="Translate any text into english", guild=self.guild)
        async def dc_translate(interaction):
            """
            This command allows you to translate any text into english.
            
            Args:
                interaction (any): The interaction object.
            """
            self.logger.info(f'Discord Command | translate | {interaction.user.name}')
            await interaction.response.send_modal(LunaTranslate())
            await self.send_log(f'{interaction.user.name} requested the translation modal')
            
        @self.tree.command(name="ask", description="Ask L.U.N.A. a question", guild=self.guild)
        async def dc_ask(interaction):
            """
            This command allows you to ask L.U.N.A. any kind of question.
            
            Args:
                interaction (any): The interaction object.
            """
            self.logger.info(f'Discord Command | ask | {interaction.user.name}')
            await interaction.response.send_modal(LunaAsk())
            await self.send_log(f'{interaction.user.name} requested the ask modal')
        
        @self.tree.command(name="support", description="Open a support ticket", guild=self.guild)
        async def dc_support(interaction):
            """
            This command allows you to open a support ticket.
            
            Args:
                interaction (any): The interaction object.
            """
            self.logger.info(f'Discord Command | support | {interaction.user.name}')
            await interaction.response.send_modal(LunaSupport())
            await self.send_log(f'{interaction.user.name} requested the support modal')


class LunaSupport(discord.ui.Modal, title='L.U.N.A. Support'):
    description = ui.TextInput(label='What do you need help with?', style=discord.TextStyle.paragraph, min_length=69,
                               max_length=1337)

    async def on_submit(self, interaction: discord):
        category = discord.utils.get(interaction.guild.categories, name="Support Tickets")
        staff_role = discord.utils.get(interaction.guild.roles, name="Dark Raven")
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True),
            staff_role: discord.PermissionOverwrite(view_channel=True)
        }
        
        ticket_no = DiscordBot.read_ticket() + 1
        channel = await guild.create_text_channel(f"ticket-{ticket_no}", category=category,
                                                  topic=f"{interaction.user.name}", overwrites=overwrites)
        
        embed_widget = discord.Embed(
            title=f"Ticket #{ticket_no}",
            description=f"**Discord User ID:** *{interaction.user.id}*\n**Discord User:** *{interaction.user.name}*\n\n**Description:**\n{self.description}",
            color=0xE91E63,
            timestamp=datetime.datetime.utcnow()
        )
        embed_widget.set_footer(text=f"2023 © Valky Dev", icon_url=f"https://exv.al/static/img/dev.webp")
        embed_widget.set_author(name=f"{interaction.user.name}", icon_url=f"{interaction.user.display_avatar.url}")
        
        await interaction.response.send_message(
            f'Thanks for your message, {interaction.user.name}!\n\nA moderator will get back to you as soon as possible.\nThanks for your patience.\n\n*~L.U.N.A. Assistant*',
            ephemeral=True)
        await channel.send(
            f'Thanks for your message, <@{interaction.user.id}>!\n\nA moderator will get back to you as soon as possible.\nThanks for your patience.\n\n*~L.U.N.A. Assistant*',
            embed=embed_widget)
        
        DiscordBot.write_ticket(ticket_no)


class LunaTranslate(discord.ui.Modal, title='L.U.N.A. Translator'):
    """
    A modal which allows you to translate text into english.
    """
    # language = ui.Select(placeholder='Select a language', max_values = 1, min_values = 1, options=[
    #     discord.SelectOption(label='Bulgarian', description='Bulgarian', value='BG'),
    #     discord.SelectOption(label='Czech', description='Czech', value='CS'),
    #     discord.SelectOption(label='Danish', description='Danish', value='DA'),
    #     discord.SelectOption(label='German', description='German', value='DE'),
    #     discord.SelectOption(label='Greek', description='Greek', value='EL'),
    #     discord.SelectOption(label='English', description='English', value='EN'),
    #     discord.SelectOption(label='Spanish', description='Spanish', value='ES'),
    #     discord.SelectOption(label='Estonian', description='Estonian', value='ET'),
    #     discord.SelectOption(label='Finnish', description='Finnish', value='FI'),
    #     discord.SelectOption(label='French', description='French', value='FR'),
    #     discord.SelectOption(label='Hungarian', description='Hungarian', value='HU'),
    #     discord.SelectOption(label='Indonesian', description='Indonesian', value='ID'),
    #     discord.SelectOption(label='Italian', description='Italian', value='IT'),
    #     discord.SelectOption(label='Japanese', description='Japanese', value='JA'),
    #     discord.SelectOption(label='Korean', description='Korean', value='KO'),
    #     discord.SelectOption(label='Lithuanian', description='Lithuanian', value='LT'),
    #     discord.SelectOption(label='Latvian', description='Latvian', value='LV'),
    #     discord.SelectOption(label='Norwegian', description='Norwegian', value='NB'),
    #     discord.SelectOption(label='Dutch', description='Dutch', value='NL'),
    #     discord.SelectOption(label='Polish', description='Polish', value='PL'),
    #     discord.SelectOption(label='Portuguese', description='Portuguese', value='PT'),
    #     discord.SelectOption(label='Romanian', description='Romanian', value='RO'),
    #     discord.SelectOption(label='Russian', description='Russian', value='RU'),
    #     discord.SelectOption(label='Slovak', description='Slovak', value='SK'),
    #     discord.SelectOption(label='Slovenian', description='Slovenian', value='SL'),
    #     discord.SelectOption(label='Swedish', description='Swedish', value='SV'),
    #     discord.SelectOption(label='Turkish', description='Turkish', value='TR'),
    #     discord.SelectOption(label='Ukrainian', description='Ukrainian', value='UK'),
    #     discord.SelectOption(label='Chinese', description='Chinese', value='ZH')
    # ])
    text_to_translate = ui.TextInput(label='Please type in your message to translate.', style=discord.TextStyle.paragraph, min_length=13, max_length=420)
    
    async def on_submit(self, interaction: discord):
        """
        This event is called when the user submits the modal form.
        
        Args:
            interaction (discord): The interaction object.
        """
        try:
            data = await LUNA.lunaTranslate(self.text_to_translate.value, "EN")
        except Exception as e:
            await interaction.response.send_message(content = f"An error occurred while translating your message: {str(e)}")
            return
        embed_widget = discord.Embed(
            title=f"L.U.N.A. Translator",
            description=f"## Text\n> {self.text_to_translate.value}\n\n## Translation\n{data['data']}",
            color=0xE91E63,
            timestamp=datetime.datetime.utcnow()
        )
        embed_widget.set_footer(text=f"2023 © Valky Dev", icon_url=f"https://exv.al/static/img/dev.webp")
        embed_widget.set_author(name=f"{interaction.user.name}", icon_url=f"{interaction.user.display_avatar.url}")
        await interaction.response.send_message(embed=embed_widget)


class LunaAsk(discord.ui.Modal, title='L.U.N.A. Assistant'):
    """
    A modal which allows you to ask L.U.N.A. a question.
    """
    question = ui.TextInput(label='Please type in your question.', style=discord.TextStyle.paragraph,
                              min_length=13, max_length=420)
                         
    async def on_submit(self, interaction: discord):
        """
        This event is called when the user submits the modal form.
        
        Args:
            interaction (discord): The interaction object.
        """
        await interaction.response.send_message(f"Processing your question, please wait...")
        
        try:
            data = await LUNA.lunaAsk(self.question.value)
        except Exception as e:
            await interaction.followup.send(content = f"An error occurred while processing your question: {str(e)}")
            return
        
        embed_widget = discord.Embed(
            title=f"L.U.N.A. Assistant",
            description=f"## Question\n> {self.question.value}\n\n## Answer\n{data['data']}",
            color=0xE91E63,
            timestamp=datetime.datetime.utcnow()
        )
        embed_widget.set_footer(text=f"2023 © Valky Dev", icon_url=f"https://exv.al/static/img/dev.webp")
        embed_widget.set_author(name=f"{interaction.user.name}", icon_url=f"{interaction.user.display_avatar.url}")
        
        await interaction.followup.send(embed = embed_widget)
