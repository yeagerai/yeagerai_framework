from typing import Optional, List

import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Option, CommandType, SubCommand

class YeagerDiscordBaseBot(commands.Bot): # AbstractInterface
    def __init__(self, command_prefix: str, fav_command:str):
        intents = discord.Intents.default()
        intents.message_content = True
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents)
        self.fav_command: Optional[str] = fav_command

    async def on_ready(self) -> None:
        print("The bot is ready!")
        synced = await self.tree.sync()
        print(f"Synced: {len(synced)} command(s)")
        if self.fav_command:
            await self.change_presence(activity=discord.Game(name=f"/{self.fav_command}"))


    def add_commands(self, new_commands: List[discord.app_commands.Command]):
        for new_command in new_commands:
            self.tree.add_command(new_command)
            