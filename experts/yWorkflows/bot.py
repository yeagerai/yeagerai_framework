import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from experts.yWorkflows.commands import create_workflow

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
async def create_workflow_command(ctx: commands.Context, *, user_prompt: str) -> None:
    await create_workflow(bot, ctx, user_prompt=user_prompt)
    return


if __name__ == "__main__":
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set")

    bot.run(BOT_TOKEN)
