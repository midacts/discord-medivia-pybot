import discord
from discord.ext import commands, tasks
from itertools import cycle
import os


TOKEN = os.getenv('TOKEN')
status = cycle(['Final Fantasy VIII', 'Super Mario 3', 'Tibia', 'Medivia', 'World of Warcraft'])
client = commands.Bot(
    command_prefix = 'med.',
    description = 'A Discord bot written in Python for the great MMORPG we all know and love named Medivia (Based on Tibia)',
    case_insensitive = True
)


# Sets the bot's status / activity
@tasks.loop(seconds=300)
async def change_status():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(next(status)))


# Logs that the bot is ready in the python console
@client.event
async def on_ready():
    change_status.start()
    print('%s\nRunning %s\n\nBot is ready.' % (discord.__version__,discord.version_info))


# Load cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


# Runs the bot
client.run(TOKEN)