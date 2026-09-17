from typing import ClassVar

import discord
from discord.ext import commands
from discord.ext.commands import Bot

import settings
from settings import TerrySettings


class SettingsCog(commands.Cog):

      command = discord.SlashCommandGroup("settings", "Terry Bot Settings :3")
      channel = command.create_subgroup("channel","Channel related settings")
      channel_settings_single:ClassVar[list] = []
      channel_settings_list:ClassVar[list]  = []
      settings_dict = settings.setting_types
      for setting in settings_dict:
          if settings_dict[setting]["type"] == "channel":
            if settings_dict[setting]["native_type"] is list:
                  channel_settings_list.append(setting)
            else:
                  channel_settings_single.append(setting)

      def __init__(self,bot):
            self.bot = bot
            self.settings = TerrySettings()
      @channel.command(name="set")
      @commands.has_permissions(administrator=True)
      async def channel_set(
                    self,
                    ctx: discord.ApplicationContext,
                    setting: discord.Option(str,choices=channel_settings_single),
                    channel: discord.Option(discord.TextChannel, "The channel to set")
                    ):
            await self.settings.set_setting_for_guild(ctx.guild_id,setting,channel.id)
            await ctx.respond(f"set '{setting}' to {channel.mention}",ephemeral=True)

def setup(bot:Bot):
     bot.add_cog(SettingsCog(bot))