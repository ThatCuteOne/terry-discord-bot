import re
from discord.ext import commands
import discord
import random


class MessageInteraction():
    def __init__(self,text, reply= True):
        self.text = text
        self.reply = reply
    async def trigger(self,message:discord.message.Message):
        if self.reply:
            await message.reply(self.text)
        else:
            await message.channel.send(self.text)
class ReactionInteraction():
    def __init__(self,reactions:list):
        self.reactions = reactions
    async def trigger(self,message:discord.message.Message):
        for r in self.reactions:
            await message.add_reaction(r)


class MessageFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message:discord.message.Message):
        if message.author.bot:
            return
       
        content = message.content.lower()
        
        # Define patterns and their responses
        pattern_responses = {
            r't+e+r+r+y+n+a+l+d+': ReactionInteraction(["6️⃣","7️⃣"]), 
            r't+e+r+r+y+|t+e+r+r+i+': ReactionInteraction(random.choice(["👋","👀","😸"])),
            r'u+n+i+v+e+r+s+e+': MessageInteraction("NOM NOM NOM"),
            r'm+e+o+w+|m+r+p+': MessageInteraction("Oliver? 👀"),
            r'o+l+i+v+e+r+': ReactionInteraction(random.choice(["😘","❤️","❤️‍🩹"]))
        }
        
        # Check each pattern
        for pattern, response in pattern_responses.items():
            if re.search(pattern, content, re.IGNORECASE):
                await response.trigger(message)

def setup(bot):
    bot.add_cog(MessageFilter(bot))