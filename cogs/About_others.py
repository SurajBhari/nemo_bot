import discord
from discord.ext import commands
import sqlite3
import asyncio
import aiosqlite
from utils.multiple_choice import BotMultipleChoice
from utils.pagination import BotEmbedPaginator
from utils.confirmation import BotConfirmation

conn = sqlite3.connect("data.db")
cur = conn.cursor()


class About_others(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(
        description="Tell or edit a little description of a person to get a little about that person"
    )
    async def desc(self, ctx, person: discord.Member = None):
        if person is None:
            person = ctx.author
        cur.execute(f"select desc from desc where id is {person.id}")
        desc = cur.fetchall()
        desc = list(sum(desc, tuple()))
        try:
            desc = desc[0]
        except IndexError:
            desc = "No description provided."
        if desc == "":
            desc = "No description provided."

        embed = discord.Embed(title=person.name, description=desc, color=0x0000FF)
        embed.set_author(name=person.display_name, icon_url=person.avatar_url)
        embed.set_thumbnail(url=person.avatar_url)
        await ctx.send(embed=embed)
        if person != ctx.author:
            return
        confirmation = BotConfirmation(ctx, 0x0000FF)
        await confirmation.confirm(
            "Seems like you are viewing your own description wanna EDIT it ?"
        )
        if confirmation.confirmed:
            await confirmation.update("Confirmed", color=0x55FF55)
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xFF5555)

        if not confirmation.confirmed:
            return

        await ctx.send(
            "Type your description right now"
            "\nIf you confirmed by mistake Type `end` to end it here. "
            "\nOr if you don't want anything type `nothing`"
        )

        def is_correct(m):
            return m.author == ctx.author and m.channel == ctx.channel

        message = await self.client.wait_for("message", check=is_correct)

        content = message.content

        if message.content.lower() == "end":
            await ctx.send("Roger. Not changing your description.")
            return

        content = content.replace('"', "")
        cur.execute(f"delete from desc where ID is {person.id}")
        conn.commit()

        if message.content.lower() != "nothing":
            cur.execute(f'insert into desc values({person.id}, "{content}")')
            conn.commit()
            await ctx.send("Done :thumbsup: \n" "Your new description reads")
            await ctx.send(content)
        else:
            await ctx.send("Removed description.")
        return

    @commands.command(description="Gives Servers's Info")
    async def server(self, ctx) -> None:
        """Gives Server's Info"""
        guild = ctx.guild
        embed = discord.Embed(
            title=guild.name, description=guild.description, color=0xB734EB,
        )
        cur.execute(
            f"SELECT COUNT(hugger_id) FROM hugs WHERE SERVER_ID = {ctx.guild.id}"
        )
        text = cur.fetchone()
        text = str(text)
        text = text.replace(")", "")
        text = text.replace("(", "")
        text = text.replace(",", "")
        desc2 = text
        cur.execute(
            f"SELECT COUNT(winker_id) FROM winks WHERE SERVER_ID = {ctx.guild.id}"
        )
        text = cur.fetchone()
        text = str(text)
        text = text.replace(")", "")
        text = text.replace("(", "")
        text = text.replace(",", "")
        desc3 = text
        offline = []
        online = []
        dnd = []
        idle = []

        for a in guild.members:
            if a.status == discord.Status.dnd:
                dnd.append(a)
            elif a.status == discord.Status.idle:
                idle.append(a)
            elif a.status == discord.Status.online:
                online.append(a)
            elif a.status == discord.Status.offline:
                offline.append(a)
        string = f":green_circle: {len(online)} \n:yellow_circle: {len(idle)} \n:red_circle: {len(dnd)}\n" \
                 f":black_circle: {len(offline)}"

        embed.add_field(name="Name", value=guild.name, inline=True)
        embed.add_field(name="ID", value=guild.id, inline=True)
        embed.add_field(name="Voice Region", value=guild.region, inline=True)
        embed.add_field(name="Owner", value=guild.owner, inline=True)
        embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
        embed.add_field(
            name="Voice Channels", value=str(len(guild.voice_channels)), inline=True
        )
        embed.add_field(
            name="Categories", value=str(len(guild.categories)), inline=True
        )
        embed.add_field(name="Members", value=str(len(guild.members)), inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Hugs Given", value=desc2, inline=False)
        embed.add_field(name="Winks Given", value=desc3, inline=False)
        embed.add_field(name="Created at", value=guild.created_at, inline=True)
        embed.add_field(name="Overall members", value=string, inline=False)
        embed.set_thumbnail(url=guild.icon_url)

        await ctx.send(embed=embed)
        return

    @commands.command(description="Gives info about someone.")
    async def profile(self, ctx, person: discord.User = None):
        """Gives info about someone."""
        if person is None:
            person = ctx.author

        async with ctx.typing():
            cur.execute(
                f"SELECT COUNT(ID) FROM infractions WHERE SERVER_ID = {ctx.guild.id} AND ID = {person.id}"
            )
            infractions_count = cur.fetchone()
            infractions_count = list(infractions_count)
            infractions_count = f"{int(infractions_count[0])}"
            # ----------------------------------------------------
            cur.execute(f"select desc from desc where id is {person.id}")
            desc_command = cur.fetchall()
            desc_command = list(sum(desc_command, tuple()))
            try:
                desc_command = desc_command[0]
            except IndexError:
                desc_command = "No description provided."
            if desc_command == "":
                desc_command = "No description provided."
            # ----------------------------------------------------
            embed = discord.Embed(
                title="INFO", description=desc_command, color=0xB734EB,
            )
            # ----------------------------------------------------
            cur.execute(
                f"SELECT COUNT(hugger_id) FROM hugs where hugged_person = {person.id}"
            )
            hugs = cur.fetchone()
            conn.commit()
            hugs = list(hugs)
            hugs = f"{int(hugs[0])}"
            # ----------------------------------------------------
            cur.execute(
                f"SELECT COUNT(winker_id) FROM winks where winked_person = {person.id}"
            )
            winks = cur.fetchone()
            conn.commit()
            winks = list(winks)
            winks = f"{int(winks[0])}"
            # ----------------------------------------------------
            embed.set_thumbnail(url=person.avatar_url)
            embed.set_author(name=person.display_name, icon_url=person.avatar_url)
            embed.add_field(name="Users Id", value=person.id, inline=False)
            embed.add_field(name="Users Name", value=person.name, inline=False)
            embed.add_field(name="Created On", value=person.created_at, inline=False)
            embed.add_field(name="Infractions", value=infractions_count, inline=False)
            embed.add_field(name="Hugs received", value=hugs, inline=False)
            embed.add_field(name="Winks received", value=winks, inline=False)

            member = ctx.guild.get_member(person.id)

            if member is not None:
                embed.add_field(
                    name="Joined this server on", value=member.joined_at, inline=False
                )
            await ctx.send(person)
            await ctx.send(embed=embed)
            return

    @commands.command(description="Gives user's avatar ")
    async def avatar(self, ctx, person: discord.User = None) -> None:
        """Gives user's avatar """
        if person is None:
            person = ctx.author
        embed = discord.Embed(title=f"{person.name}'s avatar", color=0x0000FF)
        embed.add_field(
            name="Original", value=f"[Original avatar]({person.default_avatar_url})"
        )
        embed.set_author(name=person.name, icon_url=person.avatar_url)
        embed.set_image(url=person.avatar_url)
        await ctx.send(embed=embed)
        return

    print("About_others cog loaded")


def setup(client):
    client.add_cog(About_others(client))
