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
        await draw_text(image,f"{quote}\n- {quoter}")
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer

async def render_dual_image(promt,promter,response,responder):
    image_in_bytes = await get_random_image()
    with Image.open(io.BytesIO(image_in_bytes)) as image:
        await draw_dual_text(image,f"{promt}\n- {promter}",f"{response}\n- {responder}")
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
        font = await load_font(random.randint(80,150 - len(text)//5))
        draw_text = await get_wrapped_text(text,font,1760)
        avg_color = image.resize((1, 1), resample=Image.BILINEAR).getpixel((0, 0))
        color = (255, 255, 255) if sum(avg_color) < sum((128, 128, 128)) else (0, 0, 0)
        draw_object.text((100, 100), draw_text, fill=color, font=font,align="center",anchor="la",stroke_width=5,stroke_fill=tuple((255 - rgb) for rgb in color))

async def draw_dual_text(image,promt_text, response_text):
        draw_object = ImageDraw.Draw(image)
        font_size = random.randint(80,150 - (len(promt_text) + len(response_text))//5)
        font = await load_font(font_size)
        avg_color = image.resize((1, 1), resample=Image.BILINEAR).getpixel((0, 0))
        color = (255, 255, 255) if sum(avg_color) < sum((128, 128, 128)) else (0, 0, 0)

        draw_promt = await get_wrapped_text(promt_text,font,1760)
        draw_response = await get_wrapped_text(response_text, font, 1760)
        bb = font.getbbox(draw_promt, stroke_width=5, anchor="la")
        probably_the_hight = bb[1] + bb[3]
        print(bb)
        lb = draw_promt.count("\n")

        draw_object.text((100, 100), draw_promt, fill=color, font=font,align="left",anchor="la",stroke_width=5,stroke_fill=tuple((255 - rgb) for rgb in color))
        draw_object.text((1860, 100 + probably_the_hight + lb * font_size), draw_response, fill=color, font=font,align="right",anchor="ra",stroke_width=5,stroke_fill=tuple((255 - rgb) for rgb in color))


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
    @discord.slash_command(name="quote_response", description="Quote Anything or Anyone")
    async def quote_response(
                self,
                ctx: discord.ApplicationContext,
                promt:str,
                promter:str,
                response:str,
                responder:str,
            ):
            file = File(await render_dual_image(promt,promter,response,responder),"meow.png")
            await ctx.respond(file=file)

def setup(bot:Bot):
     bot.add_cog(QuoteCog(bot))