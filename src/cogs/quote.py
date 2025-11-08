import random
import aiohttp
import io
import discord
from discord import File
from discord.ext.commands import Bot
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from discord.ext import commands

async def render_image(quote,quoter):
    image_in_bytes = await get_random_image()
    with Image.open(io.BytesIO(image_in_bytes)) as image:
        await draw_text(image,f"{quote} - {quoter}")
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer

async def load_font(size:int):
        fonts = []
        fontpath = Path('./assets/font')
        for f in fontpath.rglob("*.ttf"):
             fonts.append(str(f))
        if fonts:
             return ImageFont.truetype(random.choice(fonts),size=size)
        else:
            return ImageFont.load_default(size)

async def get_wrapped_text(text: str, font: ImageFont.ImageFont,line_length: int):
        lines = ['']
        for word in text.split(" "):
            line = f'{lines[-1]} {word}'.strip()
            if font.getlength(line) <= line_length:
                lines[-1] = line
            else:
                lines.append(word)
        return '\n'.join(lines)

async def draw_text(image,text):
        draw_object = ImageDraw.Draw(image)
        font = await load_font(random.randint(80,150))
        draw_text = await get_wrapped_text(text,font,1860)
        avg_color = image.resize((1, 1), resample=Image.BILINEAR).getpixel((0, 0))
        color = (255, 255, 255) if sum(avg_color) < sum((128, 128, 128)) else (0, 0, 0)
        draw_object.text((960, 540), draw_text, fill=color, font=font,align="center",anchor="ms",stroke_width=5,stroke_fill=tuple((255 - rgb) for rgb in color))

async def get_random_image():
    url = "https://picsum.photos/1920/1080"
    if random.randint(0,1) == 1:
         url = f"https://picsum.photos/1920/1080?blur={random.randint(1,10)}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                return content
            else:
                raise Exception(f"Failed to download image: {response.status}")

class QuoteCog(commands.Cog):
    def __init__(self,bot):
          self.bot = bot
    @discord.slash_command(name="quote_user", description="Quote a User")
    async def quote_user(
                self,
                ctx: discord.ApplicationContext,
                quote:str,
                quoter:discord.Member
            ):
            file = File(await render_image(quote,quoter.display_name),"meow.png")
            await ctx.respond(f"{quoter.mention}", allowed_mentions=discord.AllowedMentions(users=True),file=file)
    @discord.slash_command(name="quote", description="Quote Anything or Anyone")
    async def quote(
                self,
                ctx: discord.ApplicationContext,
                quote:str,
                quoter:str
            ):
            file = File(await render_image(quote,quoter),"meow.png")
            await ctx.respond(file=file)

def setup(bot:Bot):
     bot.add_cog(QuoteCog(bot))