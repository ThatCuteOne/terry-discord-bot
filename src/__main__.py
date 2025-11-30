import asyncio
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import logging

logger = logging.getLogger("Terry Bot")
logging.basicConfig(level=logging.INFO,format='[%(asctime)s] [%(name)s/%(levelname)s] %(message)s',datefmt='%H:%M:%S')

load_dotenv()

token = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)


cogs = ['cogs.quote','cogs.messages','cogs.fun','cogs.settings']

def register_cogs():
    logger = logging.getLogger("Cog Registration")
    done = 0
    for cog in cogs:
        try:
            bot.load_extension(cog)
            logger.info(f"✓ {cog} loaded successfully")
            done += 1
        except Exception as e:
            logger.exception(f"✗ Failed to load {cog}: {e}")
    logger.info(f"Sucsessfully registered cogs: {done}/{len(cogs)}")

async def setup_hook():
    register_cogs()

@bot.listen
async def on_ready():
    logger.info("Logged in as a bot {0.user}".format(bot))
    logger.info(f"Commands registered: {[cmd.name for cmd in bot.application_commands]}")
    logger.info(f"All cogs loaded: {list(bot.cogs.keys())}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Eating Universes >:3"))

def main():
    asyncio.run(setup_hook())
    bot.run(token)


main()
