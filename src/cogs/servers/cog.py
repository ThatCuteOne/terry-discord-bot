import base64
import io
import re

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from PIL import Image, ImageDraw, ImageFont

from cogs.servers.util import convert_raw_motd_to_markdown, query_server_status


class ServersCog(commands.Cog):
    def __init__(self,bot):
          self.bot = bot

    command = discord.SlashCommandGroup("mc-server", "Minecraft server related commands")
    
    @command.command(name="status", description="Get Info about a server")
    async def get_server_status(
                self,
                ctx: discord.ApplicationContext,
                ip:str,
                private:bool = True
            ):
            await ctx.defer(ephemeral=private)

            if ":" in ip:
                raw_ip, port = ip.rsplit(":",1)
            else:
                 raw_ip = ip
                 port = 25565

            try:
                status_response = query_server_status(raw_ip,port)
            except TimeoutError as e:
                 await ctx.respond(f"Connection to {ip} timed out: {e}",ephemeral=private)
                 return
            except BaseException as e:
                 await ctx.respond(f"An Unkown Error occurred while getting status: {e}",ephemeral=private)
                 return

            
            favicon:str = status_response.get("favicon")
            if favicon is not None:
                favicon = favicon.split(",")[1]     
                icon_bytes = base64.b64decode(favicon)
                img = discord.File(io.BytesIO(icon_bytes), filename="icon.png")
            else:
                image = Image.new('RGB', (64, 64), 'black')
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype("./assets/fonts/Monocraft.ttf", 56)
                text = "?"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                x = (64 - text_w) / 2 - bbox[0]
                y = (64 - text_h) / 2 - bbox[1]

                draw.text((x, y), "?", fill='white', font=font)
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                buffer.seek(0)
                img = discord.File(buffer, filename="icon.png")
                icon_bytes = buffer.getvalue()

            title = f"{ip}"
            player_info = f"{status_response.get('players').get('online')}/{status_response.get('players').get('max')}"

            motd = convert_raw_motd_to_markdown(status_response.get("description","A Minecraft Server"))
            motd_lines = motd.splitlines()
            content_length = max((len(row) for row in motd_lines), default=0)
            needed = len(title) + len(player_info)
            padding = max(0, content_length - needed)
            space_ajust_padding = padding

            title = f"{title}{' ' * int(space_ajust_padding) } {player_info}".replace(" ","\u00A0")

            motd_text = ""
            for line in motd_lines:
                motd_text += "_\u00A0_ " + line + "\n"

            motd_text = motd_text.replace(" ","\u00A0")
            motd_text = re.sub(r"§.", "", motd_text)

            embed = discord.Embed(
                  title=title,
                  description=motd_text ,
                  color=await self.get_avarage_image_color(io.BytesIO(icon_bytes))
            )
            embed.set_thumbnail(url="attachment://icon.png")        
            
            await ctx.respond(embed=embed, files=[img],ephemeral=private)

    async def get_avarage_image_color(self,bytesIO:io.BytesIO) -> discord.Colour:
        image = Image.open(bytesIO).convert("RGBA")
        pixels = list(image.getdata())
        full_pixels = [(r, g, b) for r, g, b, a in pixels if a > 0]
        if full_pixels:
            avg_r = sum(p[0] for p in full_pixels) // len(full_pixels)
            avg_g = sum(p[1] for p in full_pixels) // len(full_pixels)
            avg_b = sum(p[2] for p in full_pixels) // len(full_pixels)
            color = discord.Color.from_rgb(avg_r, avg_g, avg_b)
        else:
            color = discord.Color.blurple()
        return color

def setup(bot:Bot):
     bot.add_cog(ServersCog(bot))