import discord
from discord.ext import commands


def pas(line, pos) -> int:
    if pos == 0 or pos == line:
        return 1
    else:
        return pas(line - 1, pos - 1) + pas(line - 1, pos)


def get_triangle(toline) -> str:
    triangle = []
    for i in range(0, toline + 1):
        line = []
        for i2 in range(0, i + 1):
            line.append(str(pas(i, i2)))
        triangle.append(
            str(i) + ": " + " " * (len(str(toline)) - len(str(i))) + ", ".join(line)
        )
    return "\n".join(triangle)


class PascalTriangleCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @discord.slash_command(
        name="pascal_triangle", description="Print the Pascal Triangle from 0 to x"
    )
    async def pascal_triangle(
        self,
        ctx: discord.ApplicationContext,
        x: int,
    ):
        if x < 0:
            await ctx.respond("x can't negative")
            return
        if x > 20:
            await ctx.respond("x can't be bigger that 20")
            return
        await ctx.respond(f"Pascal Triangle from 0 to {x}:\n{get_triangle(x)}")


def setup(bot):
    bot.add_cog(PascalTriangleCog(bot))
