from discord.ext import commands
import discord
import asyncio
from data.config import unicode_emojis, cogs, close, paginator_emojis, hidden_cogs
from utils.pagination import BotEmbedPaginator


class MyHelpCommand(commands.MinimalHelpCommand):

    def get_command_signature(self, command):
        string = f"**{command.name}**" \
                 f"\n" \
                 f"\n" \
                 f"Usage-\n" \
                 f"```{self.clean_prefix}{command.qualified_name} {command.signature}```" \
                 f"\n"
        return string

    async def send_bot_help(self, mapping):
        description = (
            f"```css\n"
            f"+ [] Means optional argument.\n"
            f"+ () Means mandatory argument.\n"
            f"+ {self.clean_prefix}help [command | cog] for help on a specific command/cog"
            f"```"
        )
        embed = discord.Embed(
            description=description,
            colour=0x00ff00
        )
        cogs = [cog for cog in self.context.bot.cogs if str(cog) not in hidden_cogs]
        cogs = sorted(cogs)
        em = unicode_emojis
        em = em[:len(cogs)]
        embed.add_field(
            name="**Cogs**",
            value="\n".join([f"+ {emoji} **{cog}**" for emoji, cog in zip(em, cogs)]),
            inline=True
        )
        options = {}
        for x, y in zip(em, cogs):
            options[x] = y
        options[close] = None
        em.append(close)
        destination = self.get_destination()
        message = await destination.send(embed=embed)
        [await message.add_reaction(emoji) for emoji in em]

        def check(r, u):
            res = (r.message.id == message.id) and (u.id == self.context.author.id) and (
                    str(r.emoji) in em)
            return res

        try:
            reaction, user = await self.context.bot.wait_for('reaction_add', check=check, timeout=None)
        except asyncio.TimeoutError:
            choice = None
            return
        choice = options[str(reaction)]
        if choice:
            cog = self.context.bot.get_cog(options[str(reaction)])
            await message.delete()
            await self.send_cog_help(cog)
        else:
            await message.delete()
        return

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=command.qualified_name,
            description=f"{command.description}\n```{self.clean_prefix}{command.qualified_name} {command.signature}```",
            colour=0x00ffff
        )
        if command.aliases:
            embed.add_field(name="**Aliases**", value=" ".join([f"`{x}`" for x in command.aliases]))
        destination = self.get_destination()
        await destination.send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(
            title=group.qualified_name,
            description=f"```{self.clean_prefix}{group.qualified_name} {group.signature}```",
            colour=0x00ffff
        )
        value = ""
        if group.commands:
            for command in group.commands:
                value = value + "\n" + f"`{self.clean_prefix}{command.qualified_name} {command.signature}` " \
                                       f"  {command.description}"
            embed.add_field(name="Sub Commands", value=value)

        destination = self.get_destination()
        await destination.send(embed=embed)

    async def send_cog_help(self, cog):
        embed_list = []
        index_embed = discord.Embed(
            title="Index",
            description="\n".join([f"`{str(command.name)}` {command.description}" for command in cog.get_commands()]),
            colour=0x00ffff
        )
        index_embed.add_field(
            name="How to use.",
            value=f"{paginator_emojis[0]} - To get at the start (this page) \n"
                  f"{paginator_emojis[1]} - To get to previous page \n"
                  f"{paginator_emojis[2]} - To get to next page \n"
                  f"{paginator_emojis[3]} - Gets you to the end \n"
                  f"{close} - Stops "
        )
        embed_list.append(index_embed)
        for obj in cog.get_commands():
            embed = discord.Embed(
                title=obj.name,
                description=f"```{self.clean_prefix}{obj.qualified_name} {obj.signature}```",
                colour=0x00ffff
            )
            value = ""
            if type(obj) == discord.ext.commands.core.Group:
                for command in obj.commands:
                    value = value + "\n" + f"`{self.clean_prefix}{command.qualified_name} {command.signature}` " \
                                           f"  {command.description}"
                embed.add_field(name="Sub Commands", value=value, inline=True)
            else:
                if obj.aliases:
                    embed.add_field(name="**Aliases**", value=" ".join(f"`{x}`" for x in obj.aliases), inline=True)

            embed_list.append(embed)

        paginator = BotEmbedPaginator(self.context, embed_list)
        await paginator.run()


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._original_help_command = client.help_command
        client.help_command = MyHelpCommand()
        client.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(client):
    client.add_cog(Help(client))
