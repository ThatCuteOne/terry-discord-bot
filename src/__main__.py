import discord
import os
import random
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.default()

client = discord.Client(intents=intents)

token = os.getenv('TOKEN')

@client.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(client))









client.run(token)