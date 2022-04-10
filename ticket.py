import discord
from discord.ext import commands
import sqlite3
import asyncio
from utils.multiple_choice import BotMultipleChoice
from utils.pagination import BotEmbedPaginator
from utils.confirmation import BotConfirmation

conn = sqlite3.connect("data.db")
cur = conn.cursor()


class ticket(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(description="Configuration for Ticket system")
    @commands.has_permissions(kick_members=True)
    async def tconfig(self, ctx):
        def is_correct(m):
            return ctx.author == m.author and ctx.channel == m.channel

        await ctx.send(
            "**WARNING**\n If you have already did this config in past. we don't encourage to do it again"
            "unless this is intentional"
        )
        await ctx.send("First of all **ID** of the role that handle the tickets.")
        try:
            handler_id = await self.client.wait_for(
                "message", check=is_correct, timeout=60.0
            )
        except asyncio.TimeoutError:
            return await ctx.send("Sorry, you took too long.")
        handler_id = handler_id.content
        try:
            handler_id = int(handler_id)
        except ValueError:
            await ctx.send("That doesn't looks like a ID. you sure it is ? TRY AGAIN")
            return
        handler = ctx.guild.get_role(handler_id)
        if handler is None:
            await ctx.send("I think that role is not present here. TRY AGAIN")
            return
        await ctx.send("Nice I found the role . Now lets go forward")
        await ctx.send("Now **ID** of the category")
        try:
            category_id = await self.client.wait_for(
                "message", check=is_correct, timeout=60.0
            )
        except asyncio.TimeoutError:
            return await ctx.send("Sorry, you took too long.")
        category_id = category_id.content
        try:
            category_id = int(category_id)
        except ValueError:
            await ctx.send("That doesn't looks like a ID. you sure it is ? TRY AGAIN")
            return
        category = ctx.guild.get_channel(category_id)
        if category is None:
            await ctx.send("I think that category is not present here. TRY AGAIN")
            return

        await ctx.send("Now **ID** of the channel. where log are going")
        try:
            log_id = await self.client.wait_for(
                "message", check=is_correct, timeout=60.0
            )
        except asyncio.TimeoutError:
            return await ctx.send("Sorry, you took too long.")
        log_id = log_id.content
        try:
            log_id = int(log_id)
        except ValueError:
            await ctx.send("That doesn't looks like a ID. you sure it is ? TRY AGAIN")
            return
        log_channel = ctx.guild.get_channel(log_id)
        if log_channel is None:
            await ctx.send("I think that channel is not present here. TRY AGAIN")
            return

        embed = discord.Embed(title=ctx.guild.name, color=0x00FF00)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Role that handles it ", value=handler.mention)
        embed.add_field(name="Category ", value=category.name)
        embed.add_field(name="Log channel ", value=log_channel.mention)
        await ctx.send(embed=embed)
        confirmation = BotConfirmation(ctx, 0x0000FF)
        await confirmation.confirm("Is that it. ?")
        if confirmation.confirmed:
            await confirmation.update("Confirmed", color=0x55FF55)
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xFF5555)

        if not confirmation.confirmed:
            return

        cur.execute(f"delete from ticket where guild_id is {ctx.guild.id}")
        conn.commit()
        cur.execute(
            f"insert into ticket values({ctx.guild.id}, {handler.id}, {log_channel.id}, {category.id})"
        )
        conn.commit()
        await ctx.send(":thumbsup: Done :smile:")
        return

    @commands.command(description="Configuration for Ticket system")
    @commands.has_permissions(kick_members=True)
    async def tclose(self, ctx):
        cur.execute(f"select log from ticket where guild_id is {ctx.guild.id}")
        log = cur.fetchall()
        log = list(sum(log, tuple()))
        await ctx.send(log)
        log = log[0]
        log_channel = await self.client.fetch_channel(log)
        if log_channel.guild != ctx.guild:
            return
        conn.commit()
        messages = await ctx.channel.history(limit=1000000).flatten()
        text = ""
        for xyz in messages:
            text = f"{xyz.author} - {xyz.content} \n{text}"
        with open("log.txt", "w+") as f:
            print(text, file=f)
        await log_channel.send(file=discord.File("log.txt"))

    @commands.command(description="Configuration for Ticket system")
    async def ticket(self, ctx):
        cur.execute(f"select log from ticket where guild_id is {ctx.guild.id}")
        log = cur.fetchall()
        log = list(sum(log, tuple()))
        log = log[0]
        log_channel = await self.client.fetch_channel(log)
        if log_channel.guild != ctx.guild:
            return
        conn.commit()

        cur.execute(f"select role from ticket where guild_id is {ctx.guild.id}")
        role = cur.fetchall()[0]
        role = ctx.guild.get_role(role)
        conn.commit()

        cur.execute(f"select category from ticket where guild_id is {ctx.guild.id}")
        category = cur.fetchall()[0]
        category = ctx.guild.get_channel(category)
        conn.commit()


def setup(client):
    client.add_cog(ticket(client))
    print("Ticket cog loaded")
