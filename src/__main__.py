import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import slash_commands.quote as quote_command

load_dotenv()

token = os.getenv('TOKEN')
intents = discord.Intents.default()
bot = commands.Bot(intents=intents)


@bot.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(bot))

quote_command.setup(bot)

bot.run(token)