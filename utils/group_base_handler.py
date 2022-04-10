import discord
from discord.ext import commands

class utils:
    def __init__(self, client):
        self.client = client

    async def group_handler(self, ctx:commands.context, group:commands.Group) -> object:
        embed = discord.Embed(
            title=group.qualified_name,
            description=f"```{ctx.prefix}{group.qualified_name} {group.signature}```",
            colour=0x00ffff
        )
        value = ""
        if group.commands:
            for command in group.commands:
                value = value + "\n" + f"`{ctx.prefix}{command.qualified_name} {command.signature}` " \
                                       f"  {command.description}"
            embed.add_field(name="Sub Commands", value=value)

        return await ctx.send(embed=embed)
