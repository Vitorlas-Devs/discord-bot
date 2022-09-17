from code import interact
import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.emojis = True
intents.typing = True
intents.invites = True

bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('cookie'):
        await message.channel.send(':cookie:')

bot.run(TOKEN)
