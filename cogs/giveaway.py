import sqlite3
import discord

import random
from discord.ext import commands
import asyncio
import datetime
import aiosqlite

conn = sqlite3.connect("data.db")
cur = conn.cursor()


class giveaway(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(description="Sets up a giveaway. kick perm needed")
    @commands.has_permissions(kick_members=True)
    async def giveaway(self, message) -> None:
        """Set ups a Giveaway"""

        def is_correct(m):
            return m.author == message.author

        await message.channel.send("What's in the giveaway ?")
        try:
            giveaway_item = await self.client.wait_for(
                "message", check=is_correct, timeout=10.0
            )
        except asyncio.TimeoutError:
            return await message.channel.send("Sorry, you took too long.")
        giveaway_item = giveaway_item.content
        await message.channel.send(f"{giveaway_item}  is in the giveaway , NOTED")
        await message.channel.send(
            "Mention the channel in which you want the giveaway to be held"
        )

        def is_correct(m):
            return m.author == message.author

        try:
            giveaway_channel = await self.client.wait_for(
                "message", check=is_correct, timeout=10.0
            )
        except asyncio.TimeoutError:
            return await message.channel.send("Sorry, you took too long.")

        await message.channel.send(
            f"{giveaway_channel.content} is selected for the channel DONE!"
        )
        baxx = int(giveaway_channel.content[2 : len(giveaway_channel.content) - 1])
        channel = self.client.get_channel(baxx)

        embed = discord.Embed(
            color=0x01D277,
            title="GIVEAWAY TIME",
            description=f"Giveaway is Up \nToday's giveaway is of `{giveaway_item}` \n"
            f"React with :thumbsup: to enter ",
        )

        main_message = await channel.send(embed=embed)

        main_message_id = main_message
        giveaway_channel = int(
            giveaway_channel.content[2 : len(giveaway_channel.content) - 1]
        )
        time = str(datetime.datetime.now())
        time = time.replace("-", "")
        time = time.replace(":", "")
        time = time.replace(".", "")
        time = time.replace(" ", "")
        time = int(time)

        data = cur.execute(
            f"INSERT INTO GIVEAWAY VALUES({time}, {message.guild.id}, {giveaway_channel}, {main_message_id.id}, '{giveaway_item}')"
        )
        conn.commit()
        reactions = "\U0001f44d"
        await main_message.add_reaction(reactions)
        return

    @commands.command(
        description="Resets a accidently rolled giveaway with message id, if None then takes last."
    )
    @commands.has_permissions(kick_members=True)
    async def resetroll(self, ctx, message_id: int = None) -> None:
        """Reset a old giveaway made Givaway ."""
        if message_id is None:
            try:
                data = cur.execute(
                    f"SELECT channel_id from GIVEAWAY WHERE guild_id is {ctx.guild.id} ORDER BY time DESC"
                )
            except:
                await ctx.send("No giveaway found. 1")
                return
            giveaway_channel = list(cur.fetchone())
            giveaway_channel = giveaway_channel[0]
            data = cur.execute(
                f"SELECT message_id from GIVEAWAY WHERE guild_id is {ctx.guild.id} ORDER BY time DESC"
            )
            message_id = list(cur.fetchone())
            message_id = message_id[0]
        elif message_id is not None:
            message_id = int(message_id)
            data = cur.execute(
                f"SELECT channel_id from GIVEAWAY WHERE guild_id is {ctx.guild.id} AND message_id is {message_id} ORDER "
                f"BY "
                f"time DESC"
            )
            giveaway_channel = list(cur.fetchone())
            giveaway_channel = giveaway_channel[0]

        message_id = int(message_id)
        data = cur.execute(
            f"SELECT item from GIVEAWAY WHERE guild_id is {ctx.guild.id} AND message_id is {message_id} "
            f"ORDER BY time DESC"
        )
        item = list(cur.fetchone())
        item = item[0]

        channel = self.client.get_channel(giveaway_channel)
        message = await channel.fetch_message(message_id)
        await ctx.send("FIXED \n Don't do the same mistake again OK ?")
        embed = discord.Embed(
            color=0x01D277,
            title="GIVEAWAY TIME",
            description=f"Giveaway is Up \nToday's giveaway is of `{item}` \n"
            f"React with :thumbsup: to enter ",
        )

        await message.edit(embed=embed)
        return

    @commands.command(
        description="Rolls a giveaway with message id, if None then takes last."
    )
    @commands.has_permissions(kick_members=True)
    async def roll(self, ctx, message_id: int = None) -> None:
        """Rolls a previously made Givaway ."""
        if message_id is None:
            data = cur.execute(
                f"SELECT channel_id from GIVEAWAY WHERE guild_id is {ctx.guild.id} ORDER BY time DESC"
            )
            giveaway_channel = list(cur.fetchone())
            giveaway_channel = giveaway_channel[0]
            data = cur.execute(
                f"SELECT message_id from GIVEAWAY WHERE guild_id is {ctx.guild.id} ORDER BY time DESC"
            )
            message_id = list(cur.fetchone())
            message_id = message_id[0]
        elif message_id is not None:
            message_id = int(message_id)
            data = cur.execute(
                f"SELECT channel_id from GIVEAWAY WHERE guild_id is {ctx.guild.id} AND message_id is {message_id} "
                f"ORDER BY time DESC"
            )
            giveaway_channel = list(cur.fetchone())
            giveaway_channel = giveaway_channel[0]

        message_id = int(message_id)

        data = cur.execute(
            f"SELECT item from GIVEAWAY WHERE guild_id is {ctx.guild.id} AND message_id is {message_id} ORDER "
            f"BY time DESC "
        )
        item = list(cur.fetchone())
        item = item[0]

        channel = self.client.get_channel(giveaway_channel)
        message = await channel.fetch_message(message_id)
        print(f"message_coroutine is {message}")
        users = set()
        for reaction in message.reactions:
            async for user in reaction.users():
                print(f"(users are - {user}")
                if user.id != self.client.user.id:
                    users.add(user)
            await ctx.send(
                f"People who entered in the giveaway - : {', '.join(user.name for user in users)}"
            )

        winner = random.choice(list(users))

        text = await ctx.send(
            "Announcing the winner in 3 seconds , are you ready kids ?"
        )

        await asyncio.sleep(1)
        await text.edit(content="3!")
        await asyncio.sleep(1)
        await text.edit(content="2!")
        await asyncio.sleep(1)
        await text.edit(content="1!")
        await asyncio.sleep(1)
        await text.edit(
            content=f"{winner.mention} won.\n------------------- \nCongrats <3 ."
        )
        embed = discord.Embed(
            color=0x0279FD,  # blue
            title=f"Giveaway OVER \n",
            description=f"Winner is `{winner.name}`\nItem was `{item}`\nTotal no. of participants, `{len(users)}`",
        )
        await message.edit(embed=embed)
        return

    print("giveaway cog loaded")


def setup(client):
    client.add_cog(giveaway(client))
