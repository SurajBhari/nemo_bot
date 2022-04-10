import discord
from discord.ext import commands, tasks
from data.config import token, Personal_Server


def is_personal_server():
    def predicate(ctx):
        return ctx.guild.id == Personal_Server.guild_id

    return commands.check(predicate)


class Personal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.is_personal_server = is_personal_server

    #@commands.check(is_personal_server)
    @commands.command()
    async def role(self, ctx, role: discord.Role):
        if role.id not in Personal_Server.colored_roles:
            await ctx.send("Not one of the colored role. would not process the request.")
            return
        await ctx.author.remove_roles(*[discord.Object(x) for x in Personal_Server.colored_roles if x in [y.id for y in ctx.author.roles]])
        await ctx.author.add_roles(role)
        return


def setup(client):
    client.add_cog(Personal(client))
