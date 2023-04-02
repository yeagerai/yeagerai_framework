import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from experts.yWorkflows.commands import create_workflow
import logging


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)

# File handler for logging
file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

# Stream handler for logging to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    print("The bot is ready!")
    synced = await bot.tree.sync()
    print(f"Synced: {len(synced)} command(s)")
    await bot.change_presence(activity=discord.Game(name="/create"))


@bot.tree.command(name="create", description="Creates a new workflow")
@app_commands.describe(user_prompt="The prompt for the new workflow")
async def create_workflow_command(ctx: discord.Interaction, *, user_prompt: str) -> None:
    logger.info(f"User {ctx.user} called the create_workflow_command with user_prompt: {user_prompt}")

    await ctx.response.defer(ephemeral=True)
    bot.loop.create_task(create_workflow(bot, ctx, user_prompt=user_prompt))
    return


if __name__ == "__main__":
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set")

    bot.run(BOT_TOKEN)
