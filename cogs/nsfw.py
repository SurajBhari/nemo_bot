import discord
import nekos
from discord.ext import commands


class nsfw(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(description="Anime stuff")
    async def nekos(self, ctx, query: str):
        if not ctx.channel.is_nsfw():
            await ctx.send(
                "This is not a NSFW channel so you can't use that command here.\nContact any of the server"
                "member who have manage_channel perm to make a NSFW channel where you can use this command.",
                delete_after=15,
            )
            return
        query = query.lower()
        possible = [
            "feet",
            "yuri",
            "trap",
            "futanari",
            "hololewd",
            "lewdkemo",
            "solog",
            "feetg",
            "cum",
            "erokemo",
            "les",
            "wallpaper",
            "lewdk",
            "ngif",
            "tickle",
            "lewd",
            "feed",
            "gecg",
            "eroyuri",
            "eron",
            "cum_jpg",
            "bj",
            "nsfw_neko_gif",
            "solo",
            "kemonomimi",
            "nsfw_avatar",
            "gasm",
            "poke",
            "anal",
            "slap",
            "hentai",
            "avatar",
            "erofeet",
            "holo",
            "keta",
            "blowjob",
            "pussy",
            "tits",
            "holoero",
            "lizard",
            "pussy_jpg",
            "pwankg",
            "classic",
            "kuni",
            "waifu",
            "pat",
            "8ball",
            "kiss",
            "femdom",
            "neko",
            "spank",
            "cuddle",
            "erok",
            "fox_girl",
            "boobs",
            "random_hentai_gif",
            "smallboobs",
            "hug",
            "ero",
            "smug",
            "goose",
            "baka",
            "woof",
        ]
        if query not in possible:
            await ctx.send(
                f'Query not found list of all possible queries are \n {", ".join(possible)}',
                delete_after=20,
            )
            return
        await ctx.send(
            embed=discord.Embed(title=query, color=0x0000FF).set_image(
                url=nekos.img(query)
            )
        )


def setup(client):
    client.add_cog(nsfw(client))
    print("NSFW cog loaded")
