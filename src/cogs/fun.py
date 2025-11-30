import random
import discord
from discord.ext.commands import Bot
from discord.ext import commands

class CommandCog(commands.Cog):
    def __init__(self,bot):
          self.bot = bot
    @discord.slash_command(name="ask_terry", description="Ask Terry for their wisdom",guild_ids=["1434128644220911709"])
    async def quote_user(
                self,
                ctx: discord.ApplicationContext,
                question:str
            ):
            embed = discord.Embed(
                  title="Question",
                  description= question,
                  color=discord.Color.blurple()
            )
            embed.add_field(name="",value=await get_answer(),inline=False)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            await ctx.respond(embed=embed, allowed_mentions=discord.AllowedMentions.all())


def setup(bot:Bot):
     bot.add_cog(CommandCog(bot))


async def get_answer():
      responses = [
            "*licks your face*",
            "*bonks you*",
            "*bites your toe*",
            "*terry sounds*",
            "*squeaks extremly cutely*",
            "*farts*",
            "*pounces on your knees*",
            "*retracts into shell*"
      ]
      return random.choice(responses)