from code import interact
import discord
from discord.ext import commands
import asyncio
import os

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

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('-hello'):
        await message.channel.send('Hello!')

client.run('MTAxODQ0ODA3NTE4Mzg5MDQ1NA.G5zBR8.qMJcFCWR1uh20aZ0JGvlUDntfwlSYSU3AankY8')
