import asyncio
import discord
from discord.ext import commands, tasks
from utils.multiple_choice import BotMultipleChoice
from utils.pagination import BotEmbedPaginator
from utils.confirmation import BotConfirmation
import datetime

import aiohttp
import json
import sqlite3

conn = sqlite3.connect("data.db")
cur = conn.cursor()


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


class Live(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check.start()

    @commands.command(description="Main Help Command for Live")
    async def live(self, ctx):
        embeds = []
        cog_ = self.client.get_cog("Live")
        commands_ = list(cog_.get_commands())
        for c in commands_:
            if c.description == "" or c.description is None:
                desc = "None"
            else:
                desc = c.description
            a = discord.Embed(title=c.name, description=desc + "\n\n", color=0x00FF00)
            a.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            a.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
            a.add_field(name="Usage", value=f"```{ctx.prefix}{c} {c.signature}```")
            embeds.append(a)
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()

    @commands.has_permissions(kick_members=True)
    @commands.command(description="Start the setup")
    async def liveadd(self, ctx):
        async with aiohttp.ClientSession() as session:
            await ctx.send(
                "Welcome and lets continue adding a youtube channel to get notified."
            )

            def is_correct(m):
                return m.author == ctx.author

            await ctx.send("First of all I want the youtube link to the **Channel**")

            try:
                message = await self.client.wait_for(
                    "message", check=is_correct, timeout=60.0
                )
            except asyncio.TimeoutError:
                return await ctx.send("Sorry, you took too long.")
            link = message.content
            if "https://www.youtube.com/channel/" not in link:
                await ctx.send(
                    "INVALID youtube link for it to be a valid link it should start "
                    'with "https://www.youtube.com/channel/"'
                )
                return
            if link[-1] == "/":
                list1 = list(link)
                list1[-1] = ""
                link = "".join(list1)

            await ctx.send(
                "What should the message be when youtuber went live ? Default is \n Hey {role_to_be_pinged} "
                " {channel_name} Just posted a video catch it here :- {link} \n If you want this type **default** \n"
                "If you are using your own message make sure to use **{link}** , **{role_to_be_pinged}** and "
                "{channel_name}"
                "to make sure your message also contain those."
            )
            try:
                live_message = await self.client.wait_for(
                    "message", check=is_correct, timeout=60.0
                )
            except asyncio.TimeoutError:
                return await ctx.send("Sorry, you took too long.")
            live_message = live_message.content
            if "default" == live_message.lower():
                live_message = "Hey {role_to_be_pinged} , {channel_name} Just posted a video catch it here :- {link}"
                await ctx.send(
                    "**ID** of the role to be pinged ? You can get it by going in server setting and right clicking "
                    "on the role and COPY ID"
                )
            if "{role_to_be_pinged}" in live_message:
                try:
                    role = await self.client.wait_for(
                        "message", check=is_correct, timeout=60.0
                    )
                except asyncio.TimeoutError:
                    return await ctx.send("Sorry, you took too long.")
                role = role.content
                try:
                    role = int(role)
                except ValueError:
                    await ctx.send("I said ID!!! Retry ")
                    return

                role2 = ctx.guild.get_role(role)
                if role2 is None:
                    await ctx.send("Role not found!! Retry")
                    return

            if "{role_to_be_pinged}" not in live_message:
                role = 0
                role2 = "None"

            await ctx.send(
                "Finally the **ID** of the text channel you want notification be in"
            )
            try:
                channel = await self.client.wait_for(
                    "message", check=is_correct, timeout=60.0
                )
            except asyncio.TimeoutError:
                return await ctx.send("Sorry, you took too long.")
            channel = channel.content
            try:
                channel = int(channel)
            except ValueError:
                await ctx.send("I said ID!!! Retry ")
                return

            channel2 = ctx.guild.get_channel(channel)
            if channel2 is None:
                await ctx.send("Channel not found!! Retry")
                return

            embed = discord.Embed(
                title="Done",
                description="Your Setup Initialized Successfully",
                color=0x00FF00,
            )
            channel_id = link
            channel_id = list(channel_id)
            channel_id = " ".join(channel_id)
            # channel_id = channel_id.replace('h t t p s : / / w w w . y o u t u b e . c o m / u s e r /', '')
            channel_id = channel_id.replace(
                "h t t p s : / / w w w . y o u t u b e . c o m / c h a n n e l /", ""
            )
            channel_id = channel_id.replace(" ", "")

            html = await fetch(
                session,
                f"https://www.googleapis.com/youtube/v3/search?key"
                f"=AIzaSyDI48cMvIpr647K7D3_6VJ8GV_ngtJHO6M&channelId="
                f"{channel_id}&part=snippet,id&order=date&maxResults=2",
            )
            data = json.loads(html)
            videoId = data["items"][0]["id"]["videoId"]

            embed.add_field(name="Youtube link", value=link)
            embed.add_field(name="Message", value=live_message)
            embed.add_field(name="Role That will got Pinged", value=role2)
            embed.add_field(name="Channel it goes in", value=channel2)
            embed.add_field(
                name="Whose Last video was",
                value=f"https://www.youtube.com/watch?v={videoId}",
            )
            embed.set_image(
                url=data["items"][0]["snippet"]["thumbnails"]["high"]["url"]
            )
            await ctx.send(embed=embed)
            cur.execute(
                f'insert into livedata values({ctx.guild.id}, {channel}, {role}, "{channel_id}", "{videoId}", "{live_message}" )'
            )
            conn.commit()
            """"guild_id INT(50), channel INT(50), role INT(50), link VARCHAR, last VARCHAR, message VARCHAR) """

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def livelist(self, ctx):
        async with aiohttp.ClientSession() as session:
            cur.execute(f"select channel from livedata where guild_id = {ctx.guild.id}")
            guild_id_list = cur.fetchall()
            conn.commit()
            guild_id_list = list(sum(guild_id_list, tuple()))
            cur.execute(f"select channel from livedata where guild_id = {ctx.guild.id}")
            channel_list = cur.fetchall()
            conn.commit()
            channel_list = list(sum(channel_list, tuple()))
            temp_list = channel_list
            channel_list = []
            for x in temp_list:
                channe = self.client.get_channel(x)
                channel_list.append(channe.mention)
            cur.execute(f"select role from livedata where guild_id = {ctx.guild.id}")
            role_list = cur.fetchall()
            conn.commit()
            role_list = list(sum(role_list, tuple()))
            temp_list = role_list
            role_list = []
            for x in temp_list:
                if x == 0:
                    roll = ""
                else:
                    roll = ctx.guild.get_role(x)
                    if roll.is_default():
                        roll = str(roll)
                    else:
                        roll = str(roll.mention)
                role_list.append(roll)
            cur.execute(f"select link from livedata where guild_id = {ctx.guild.id}")
            link_list = cur.fetchall()
            conn.commit()
            link_list = list(sum(link_list, tuple()))
            temp_list = link_list
            link_list = []
            for x in temp_list:
                x = f"https://www.youtube.com/channel/{x}"
                link_list.append(x)

            cur.execute(f"select last from livedata where guild_id = {ctx.guild.id}")
            last_list = cur.fetchall()
            conn.commit()
            last_list = list(sum(last_list, tuple()))
            temp_list = last_list
            last_list = []
            for x in temp_list:
                last_list.append(f"https://www.youtube.com/watch?v={x}")
            cur.execute(f"select message from livedata where guild_id = {ctx.guild.id}")
            message_list = cur.fetchall()
            conn.commit()
            message_list = list(sum(message_list, tuple()))
            strin = "| Channel where messages goes | role that get pinged | Channel link | last video link | Message |"

            for guild_id, channel, role, link, last, message in zip(
                guild_id_list,
                channel_list,
                role_list,
                link_list,
                last_list,
                message_list,
            ):
                # if ctx.guild == guild:
                strin = strin + "\n" + f"{channel} {role} {link} {last} {message}"

            embed = discord.Embed(title="Here!", description=strin, color=0x0000FF)
            await ctx.send(embed=embed)

    @commands.has_permissions(kick_members=True)
    @commands.command(
        description="Delete the announcement for vid with youtube channel link"
    )
    async def livedel(self, ctx, channel):
        cur.execute(
            f'delete from livedata where link like "%{channel}%" and guild_id = {ctx.guild.id}'
        )
        conn.commit()
        if "https://www.youtube.com/" in ctx.message.content:
            await ctx.send(
                "I don't need whole link I only need channel ID for example for "
                "https://www.youtube.com/channel/UCbZZmB8L3IEHutGbvpWo9Ow it will be **UCbZZmB8L3IEHutGbvpWo9Ow**"
            )
            return

        await ctx.send("Done if there was one.")

    @tasks.loop(minutes=15)
    async def check(self):
        async with aiohttp.ClientSession() as session:
            print(
                f"{datetime.datetime.now()} - Checking if someone uploaded a video or not."
            )
            cur.execute(f"select guild_id from livedata")
            guild_id_list = cur.fetchall()
            guild_id_list = list(sum(guild_id_list, tuple()))
            cur.execute(f"select channel from livedata")
            channel_list = cur.fetchall()
            channel_list = list(sum(channel_list, tuple()))
            cur.execute(f"select role from livedata")
            role_list = cur.fetchall()
            role_list = list(sum(role_list, tuple()))
            cur.execute(f"select link from livedata")
            link_list = cur.fetchall()
            link_list = list(sum(link_list, tuple()))
            cur.execute(f"select last from livedata")
            last_list = cur.fetchall()
            last_list = list(sum(last_list, tuple()))
            cur.execute(f"select message from livedata")
            message_list = cur.fetchall()
            message_list = list(sum(message_list, tuple()))
            for guild_id, channel, role, link, last, message in zip(
                guild_id_list,
                channel_list,
                role_list,
                link_list,
                last_list,
                message_list,
            ):
                html = await fetch(
                    session,
                    f"https://www.googleapis.com/youtube/v3/search?key"
                    f"=AIzaSyALPlCtSmPNUBm7FnjcRPGnEDsb5kBgbvI&channelId="
                    f"{link}&part=snippet,id&order=date&maxResults=2",
                )
                data = json.loads(html)
                videoId = data["items"][0]["id"]["videoId"]
                if videoId != last:
                    channel = self.client.get_channel(channel)
                    guild = self.client.get_guild(guild_id)
                    if role == 0:
                        role = ""
                    else:
                        role = guild.get_role(role)
                        if not role.is_default():
                            role = role.mention
                        else:
                            role = str(role)
                        message = message.replace("{role_to_be_pinged}", role)
                    message = message.replace(
                        "{link}", f"https://www.youtube.com/watch?v={videoId}"
                    )
                    message = message.replace(
                        "{channel_name}", data["items"][0]["snippet"]["channelTitle"]
                    )
                    embed = discord.Embed(
                        title=data["items"][0]["snippet"]["title"],
                        description=data["items"][0]["snippet"]["description"],
                        color=0xFF0000,
                    )
                    embed.set_image(
                        url=data["items"][0]["snippet"]["thumbnails"]["high"]["url"]
                    )
                    await channel.send(message, embed=embed)
                    cur.execute(
                        f'update livedata set last = "{videoId}" where guild_id is {guild_id} and link is "{link}"'
                    )
                    conn.commit()

    @commands.command(description="ONLY FOR BOT OWNER")
    @commands.is_owner()
    async def manualcheck(self, ctx):
        await self.check.invoke()


def setup(client):
    client.add_cog(Live(client))

    print("LIVE COG LOADED")
