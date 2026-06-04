from datetime import timedelta,datetime
import re
from typing import Union
from discord.ext import commands
import discord
import random

class MessageInteraction():
    def __init__(self,text, reply= True, cooldown:timedelta=timedelta(minutes=0)):
        self.text = text
        self.reply = reply
        self.cooldown = cooldown
        self.last_used = None

    def is_on_cooldown(self) -> bool:
        if self.last_used is None: return False
        time_since_last = datetime.now() - self.last_used
        if time_since_last > self.cooldown: return False
        return True

    async def trigger(self,message:discord.message.Message):
        if self.is_on_cooldown(): return
        self.last_used = datetime.now()
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

    def register_pattern(self,regex:str,interaction:Union[ReactionInteraction,MessageInteraction]):
        self.patterns[regex] = interaction


    def __init__(self, bot):
        self.patterns = {}
        self.bot = bot

        # register pattern interactions
        self.register_pattern(r't+e+r+r+y+n+a+l+d+', ReactionInteraction(["6️⃣","7️⃣"]))
        self.register_pattern(r't+e+r+r+y+|t+e+r+r+i+', ReactionInteraction(random.choice(["👋","👀","😸"])))
        self.register_pattern(r'u+n+i+v+e+r+s+e+', MessageInteraction("NOM NOM NOM"))
        self.register_pattern(r'm+e+o+w+|m+r+p+', MessageInteraction("Oliver? 👀",True,timedelta(minutes=1))),
        self.register_pattern(r'o+l+i+v+e+r+', ReactionInteraction(random.choice(["😘","❤️","❤️‍🩹"])))
        self.register_pattern(r'b+l+u+b', ReactionInteraction(["🐙"]))
    
    @commands.Cog.listener()
    async def on_message(self, message:discord.message.Message):
        if message.author.bot:
            return
        content = message.content
        
        # Check each pattern
        for pattern, response in self.patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                await response.trigger(message)

def setup(bot):
    bot.add_cog(MessageFilter(bot))