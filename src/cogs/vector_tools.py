from io import BytesIO
import re
from PIL import Image
from discord import File
import discord
from discord.ext import commands
from sympy import preview

from vector_tools import Line, Plane, Vector

vector_regex = "^\\((-?([0-9]|\\.)+,?)+\\)$"
sep = "(\\+|-).\\*"
line_regex = vector_regex[:-1] + sep + vector_regex[1:]
plane_regex1 = vector_regex[:-1] + sep + vector_regex[1:-1] + sep + vector_regex[1:]
part = "((-|\\+)?[0-9]+(\\*)?{var})?"
plane_regex2 = f"^\\(.-{vector_regex[1:-1]}\\)\\*{vector_regex[1:-1]}=0$"
plane_regex3 = (
    f"^{part.format(var='x') + part.format(var='y') + part.format(var='z')}=[0-9]+$"
)
plane_regex = f"({plane_regex1}|{plane_regex2}|{plane_regex3})"


def to_vector(expression: str) -> Vector:
    return Vector(expression[1:-1].split(","))


def to_line(expression: str) -> Line:
    return Line(
        Vector(re.sub("\\).*", "", expression)[1:].split(",")),
        Vector(re.sub(".*\\(", "", expression)[:-1].split(",")),
    )


def to_plane(expression: str) -> Plane:
    if re.match(plane_regex1, expression):
        return Plane(
            [
                Vector(re.sub("\\).*", "", expression)[1:].split(",")),
                Vector(re.sub("\\).*", "", expression.split("*")[1])[1:].split(",")),
                Vector(re.sub(".*\\(", "", expression)[:-1].split(",")),
            ]
        )
    elif re.match(plane_regex2, expression):
        return Plane(
            [
                Vector(re.sub("\\).*", "", expression)[4:].split(",")),
                Vector(re.sub("\\).*", "", expression.split("*")[1])[1:].split(",")),
            ]
        )
    else:
        coords = []
        string = expression.split("=")[0]
        chars = ["x", "y", "z"]
        for i, c in enumerate(chars):
            if re.match(f".*{c}.*", string.split("=")[0]):
                coords.append(
                    re.sub(f"{c}.*", "", string.split("=")[0]).split(chars[i - 1])[-1]
                )
                string = re.sub(f"(-|\\+)?[0-9]+{c}", "", string)
            else:
                coords.append("0")

        return Plane([coords, expression.split("=")[-1]])


def get_image(input: BytesIO) -> BytesIO:
    with Image.open(input) as image:
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
    return buffer


async def callback(ctx: discord.ApplicationContext, input: str) -> None:
    expression = re.sub(" ", "", input).split(";")
    assert len(expression) in [1, 2]
    obj = BytesIO()
    if all([re.match(vector_regex, i) for i in expression]):
        vector = to_vector(expression[0])
        preview(
            f"$${vector.tex}$$",
            output="png",
            outputbuffer=obj,
            viewer="BytesIO",
        )
        # if len(expression) == 1:
        #     pass
        # else:
        #     vector2 = to_vector(expression[1])
    elif all([re.match(line_regex, i) for i in expression]):
        line = to_line(expression[0])
        if len(expression) == 1:
            preview(f"$${line.tex}$$", output="png", outputbuffer=obj, viewer="BytesIO")
            await ctx.respond(file=File(get_image(obj), "image.png"))
        else:
            line2 = to_line(expression[1])
            preview(
                f"$${line.tex} and {line2.tex}$$",
                output="png",
                outputbuffer=obj,
                viewer="BytesIO",
            )
            await ctx.respond(
                "Relation of those lines:", file=File(get_image(obj), "image.png")
            )
            probe = line.probe_line(line2)
            match probe["relation"]:
                case 0:
                    await ctx.respond("The lines are identical")
                case 1:
                    await ctx.respond(
                        f"The lines are parallel and {round(probe['distance'], 2)} length units apart from each other."
                    )
                case 2:
                    await ctx.respond(
                        f"The lines intersect at the point S(){'|'.join(str(i) for i in probe['intersection'])}) at an angle of {round(probe['angle'], 2)}°."
                    )
                case 3:
                    await ctx.respond(
                        f"The lines are skew and {round(probe['distance'], 2)} length units apart from each other."
                    )

    elif all([re.match(plane_regex, i) for i in expression]):
        plane = to_plane(expression[0])
        preview(
            f"$${plane.normal_tex}$$", output="png", outputbuffer=obj, viewer="BytesIO"
        )
        # if len(expression) == 1:
        #     pass
        # else:
        #     plane2 = to_plane(expression[1])
    else:
        return


class VectorToolsCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @discord.slash_command(
        name="vector_tools", description="A little test for vector tools"
    )
    async def latex_image(self, ctx: discord.ApplicationContext, exp: str):
        await callback(ctx, exp)
        # render = callback(exp)
        # if render is not None:
        #     file = File(get_image(render), "render.png")
        #     await ctx.respond(file=file)
        # else:
        #     await ctx.respond("Invalid input")


def setup(bot):
    bot.add_cog(VectorToolsCog(bot))
