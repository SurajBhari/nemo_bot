import discord
from discord.ext import commands
import sqlite3
import datetime
import asyncio
from collections import Counter
from utils.multiple_choice import BotMultipleChoice
from utils.pagination import BotEmbedPaginator
from utils.confirmation import BotConfirmation
import matplotlib.pyplot as plt
from typing import Union
import json
from discord.ext.commands.cooldowns import BucketType


color = "white"
plt.rcParams.update({"font.size": 13})
plt.rcParams.update({"text.color": color, "axes.labelcolor": color})
plt.rcParams["text.color"] = color
plt.rcParams["axes.labelcolor"] = color
plt.rcParams["xtick.color"] = color
plt.rcParams["ytick.color"] = color


def sqlconvert(a: list):
    return sum(a, tuple())


conn = sqlite3.connect("data.db")
cur = conn.cursor()


class Moderating(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.content:
            return
        cur.execute(f"select channel_id from log where guild_id is {message.guild.id}")
        channel_id = cur.fetchall()
        conn.commit()
        channel_id = list(sqlconvert(channel_id))
        try:
            channel_id = channel_id[0]
        except IndexError:
            return

        channel = message.guild.get_channel(int(channel_id))
        embed = discord.Embed(title="Deleted message", color=0x0000FF,)
        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name="Channel", value=message.channel.mention)
        embed.add_field(name="Author", value=message.author.mention)
        content = message.content
        if len(content) > 1000:
            await channel.send("__Deleted message__ message too big so no embed")
            await channel.send(content)
            return

        embed.add_field(name="Content", value=content)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        cur.execute(
            f"select channel_id from log where guild_id is {messages[0].guild.id}"
        )
        channel_id = cur.fetchall()
        conn.commit()
        channel_id = list(sqlconvert(channel_id))
        try:
            channel_id = channel_id[0]
        except IndexError:
            return
        text = ""
        for xyz in messages:
            text = f"{text} \n{xyz.author} - {xyz.content}"
        with open("log.txt", "w+") as f:
            print(text, file=f)

        channel = messages[0].guild.get_channel(int(channel_id))
        embed = discord.Embed(title="Bulk delete", color=0x0000FF,)
        embed.set_author(
            name=messages[0].guild.name, icon_url=messages[0].guild.icon_url
        )
        embed.add_field(name="Channel", value=messages[0].channel.mention)
        await channel.send(embed=embed)
        await channel.send(file=discord.File("log.txt"))

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        cur.execute(f"select channel_id from log where guild_id is {channel.guild.id}")
        channel_id = cur.fetchall()
        conn.commit()
        channel_id = list(sqlconvert(channel_id))
        try:
            channel_id = channel_id[0]
        except IndexError:
            return
        channel_log = channel.guild.get_channel(int(channel_id))
        embed = discord.Embed(title="New Channel creted", color=0x00FF00)
        embed.add_field(name="Channel is", value=channel.mention)
        embed.add_field(name="Name", value=channel.name)
        embed.add_field(name="Permission synced", value=channel.permissions_synced)
        embed.add_field(name="Position", value=channel.position)
        await channel_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        cur.execute(f"select channel_id from log where guild_id is {channel.guild.id}")
        channel_id = cur.fetchall()
        conn.commit()
        channel_id = list(sqlconvert(channel_id))
        try:
            channel_id = channel_id[0]
        except IndexError:
            return
        channel_log = channel.guild.get_channel(int(channel_id))
        embed = discord.Embed(title="Channel deleted", color=0x00FF00)
        embed.add_field(name="Channel is", value=channel.mention)
        embed.add_field(name="Name", value=channel.name)
        embed.add_field(name="Category", value=channel.category)
        embed.add_field(name="Permission synced", value=channel.permissions_synced)
        embed.add_field(name="Position", value=channel.position)
        await channel_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        cur.execute(f"select channel_id from log where guild_id is {member.guild.id}")
        channel_id = cur.fetchall()
        conn.commit()
        channel_id = list(sqlconvert(channel_id))
        try:
            channel_id = channel_id[0]
        except IndexError:
            return
        channel = member.guild.get_channel(int(channel_id))
        

        if before.channel is None:
            embed = discord.Embed(title="Connected voice", color=0x00FF00)
            embed.set_author(name=member.name, icon_url=member.avatar_url)
            embed.add_field(
                name="To",
                value=f"{after.channel.name}"
                )
        elif after.channel is None:
            embed = discord.Embed(title="Disconnected voice", color=0xFF0000)
            embed.set_author(name=member.name, icon_url=member.avatar_url)
            embed.add_field(
                name="From",
                value=f"{before.channel.name}"
                )
        elif ((before.channel == after.channel) and (before.channel is not None) and (after.channel is not None)):
            embed = discord.Embed(title="Changed Voice state", color=0x0000ff)
            embed.set_author(name=member.name, icon_url=member.avatar_url)
            embed.add_field(name="Channel", value=f"{before.channel.name}")
            chr = ""
            if before.self_deaf != after.self_deaf:
                #Deafened/Undeafened themself
                if after.self_deaf:
                    chr = "Self Deafened"
                elif before.self_deaf:
                    chr = "Self Undeafened"
                pass

            elif before.self_mute != after.self_mute:
                #Muted/Unmuted themself
                if after.self_mute:
                    chr = "Self Mutted"
                elif before.self_mute:
                    chr = "Self Unmutted"
                pass
            
            elif before.self_stream != after.self_stream:
                #Started/stopped streaming
                if after.self_stream:
                    chr = "Started Streaming"
                elif before.self_stream:
                    chr = "Stopped Streaming"
                pass
            elif before.self_video != after.self_video:
                #Started/Stopped cam
                if after.self_video:
                    chr = "Turned on Camera"
                elif before.self_video:
                    chr = "Turned off Camera"
                pass
            elif before.deaf != after.deaf:
                #Server Deafned/undeafend 
                if after.deaf:
                    chr = "Server Deafned"
                elif before.deaf:
                    chr = "Server Undeafned"
                pass
            elif before.mute != after.mute:
                #Server Muted/Unmuted themself
                if after.mute:
                    chr = "Server Mutted"
                elif before.mute:
                    chr = "Server Unmutted"
                pass
            
            else:
                chr = "Unknown Event"
            
            embed.title = chr
        
        elif (before.channel is not None) and (after.channel is not None):
            embed = discord.Embed(title="Moved voice", color=0x0000FF)
            embed.set_author(name=member.name, icon_url=member.avatar_url)

            embed.add_field(
                name="From",
                value=f"{before.channel.name}"
                )
            embed.add_field(
                name="To",
                value=f"{after.channel.name}"
                )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        cur.execute(f"select channel_id from log where guild_id is {before.guild.id}")
        channel_id = cur.fetchall()
        conn.commit()
        channel_id = list(sqlconvert(channel_id))
        try:
            channel_id = channel_id[0]
        except IndexError:
            return
        channel = before.guild.get_channel(int(channel_id))
        embed = discord.Embed(title="Message edited", color=0x0000FF)
        embed.set_author(name=before.author.name, icon_url=before.author.avatar_url)
        embed.add_field(name="Before", value=f"```{before.content}```", inline=False)
        embed.add_field(name="After", value=f"```{after.content}```", inline=False)
        embed.add_field(name="Jump URL", value=after.jump_url, inline=False)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        cur.execute(f"select channel_id from log where guild_id is {member.guild.id}")
        channel_id = cur.fetchall()
        conn.commit()
        channel_id = list(sqlconvert(channel_id))
        try:
            channel_id = channel_id[0]
        except IndexError:
            return
        channel = member.guild.get_channel(int(channel_id))
        embed = discord.Embed(
            title="New Member", description=str(member), color=0x00FF00
        )
        embed.set_author(name=member.name, icon_url=member.avatar_url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        cur.execute(f"select channel_id from log where guild_id is {member.guild.id}")
        channel_id = cur.fetchall()
        conn.commit()
        channel_id = list(sqlconvert(channel_id))
        try:
            channel_id = channel_id[0]
        except IndexError:
            return
        channel = member.guild.get_channel(int(channel_id))
        embed = discord.Embed(
            title="Member left", description=str(member), color=0x00FF00
        )
        embed.set_author(name=member.name, icon_url=member.avatar_url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        cur.execute(f"select channel_id from log where guild_id is {after.guild.id}")
        channel_id = cur.fetchall()
        conn.commit()
        channel_id = list(sqlconvert(channel_id))
        try:
            channel_id = channel_id[0]
        except IndexError:
            return
        channel = after.guild.get_channel(int(channel_id))
        embed = discord.Embed(title="Role updated", color=after.color)
        embed.add_field(name="Role is", value=after.mention)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        cur.execute(f"select channel_id from log where guild_id is {guild.id}")
        channel_id = cur.fetchall()
        conn.commit()
        channel_id = list(sqlconvert(channel_id))
        try:
            channel_id = channel_id[0]
        except IndexError:
            return
        channel = guild.get_channel(int(channel_id))
        embed = discord.Embed(title="Member Banned", color=0xFF0000)
        embed.add_field(name="Name", value=user.name)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        cur.execute(f"select channel_id from log where guild_id is {guild.id}")
        channel_id = cur.fetchall()
        conn.commit()
        channel_id = list(sqlconvert(channel_id))
        try:
            channel_id = channel_id[0]
        except IndexError:
            return
        channel = guild.get_channel(int(channel_id))
        embed = discord.Embed(title="Member Unbanned", color=0x00FF00)
        embed.add_field(name="Name", value=user.name)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        if invite.guild is None:
            return
        cur.execute(f"select channel_id from log where guild_id is {invite.guild.id}")
        channel_id = cur.fetchall()
        conn.commit()
        channel_id = list(sqlconvert(channel_id))
        try:
            channel_id = channel_id[0]
        except IndexError:
            return
        channel = invite.guild.get_channel(int(channel_id))
        embed = discord.Embed(title="New Invite created", color=0x00FF00)
        embed.add_field(name="code", value=invite.code)
        embed.add_field(name="Created at", value=invite.created_at)
        embed.add_field(name="Temp?", value=invite.temporary)
        embed.add_field(name="Max uses", value=invite.max_uses)
        embed.set_author(name=invite.inviter.name, icon_url=invite.inviter.avatar_url)
        embed.add_field(name="URL", value=invite.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        if invite.guild is None:
            return
        cur.execute(f"select channel_id from log where guild_id is {invite.guild.id}")
        channel_id = cur.fetchall()
        conn.commit()
        channel_id = list(sqlconvert(channel_id))
        try:
            channel_id = channel_id[0]
        except IndexError:
            return
        channel = invite.guild.get_channel(int(channel_id))
        embed = discord.Embed(title="Invite deleted", color=0x00FF00)
        embed.add_field(name="code", value=invite.code)
        embed.add_field(name="Created at", value=invite.created_at)
        embed.add_field(name="Temp?", value=invite.temporary)
        embed.add_field(name="Max uses", value=invite.max_uses)
        embed.set_author(name=invite.inviter.name, icon_url=invite.inviter.avatar_url)
        embed.add_field(name="URL", value=invite.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.client.user.id:
            return
        if message.author.bot:
            return

        if not message.guild:
            return
        if not message.content:
            return

        cur.execute(f"SELECT word FROM block WHERE server_id is {message.guild.id} ")
        words = cur.fetchall()
        conn.commit()
        words = sqlconvert(words)
        if words == [""]:
            pass
        else:
            content = message.content.split(" ")
            for x in content:
                for a in words:
                    if a == x.lower():
                        if message.author.id != 355658987372281856:
                            await message.delete()
                            embed = discord.Embed(
                                title="NOOOOO!",
                                description="That word is not allowed here.",
                                color=0xFF0000,
                            )
                            embed.set_author(
                                name=message.author, icon_url=message.author.avatar_url
                            )
                            embed.set_footer(
                                text=message.guild.name, icon_url=message.guild.icon_url
                            )
                            await message.channel.send(embed=embed, delete_after=5)
                            print(f"Deleted a message cuz it contain {a}")
                            return

        cur.execute(f"SELECT trigger FROM reply where SERVER_ID is {message.guild.id}")
        list_ = cur.fetchall()
        content = message.content.lower()
        conn.commit()
        list_ = sqlconvert(list_)
        if str(content) in list_:
            cur.execute(
                f'SELECT value FROM reply WHERE SERVER_ID IS {message.guild.id} AND trigger is "{content}"'
            )
            reply = cur.fetchone()
            reply = reply[0]
            await message.channel.send(reply)
            conn.commit()
        cur.execute(
            f"SELECT word FROM warn_words where SERVER_ID is {message.guild.id}"
        )
        list_ = cur.fetchall()
        conn.commit()
        list_ = sqlconvert(list_)
        content = message.content.lower()
        if str(content) in list_:
            cur.execute(
                f"select mod from warn_words where SERVER_ID is {message.guild.id}"
            )
            a = cur.fetchone()
            a = a[0]
            role = message.guild.get_role(a)
            embed = discord.Embed(
                title=f"Someone said {message.content} In {message.guild.name}",
                description=f"[Visit original message]({message.jump_url})",
                color=0xFF0000,
            )
            embed.set_author(
                name=message.author.name, icon_url=message.author.avatar_url
            )
            for a in role.members:
                await a.send(embed=embed)

    @commands.command(description="Set logging channel")
    async def log(self, ctx, channel: discord.TextChannel = None) -> None:
        cur.execute(f"delete from log where guild_id is {ctx.guild.id} ")
        conn.commit()
        if channel is None:
            await ctx.send("Not logging anymore")
            return
        cur.execute(f"insert into log values({ctx.guild.id}, {channel.id})")
        conn.commit()
        await ctx.send(f"Toggled logging on {channel.mention}")
        return

    @commands.command(description="Set an custom prefix for me.")
    @commands.has_permissions(kick_members=True)
    async def prefix(self, ctx, *, prefix: str = ">") -> None:
        cur.execute(f"delete from prefixes where guild_id is {ctx.guild.id} ")
        conn.commit()
        cur.execute(f'insert into prefixes values("{prefix}", {ctx.guild.id})')
        await ctx.send(f"Prefix is now `{prefix}`")
        conn.commit()
        try:
            await ctx.guild.me.edit(nick=f"[{prefix}] {self.client.user.name}")
        except discord.Forbidden:
            pass
        return

    @commands.command(description="Mass delete messages")
    @commands.has_permissions(kick_members=True)
    async def purge(self, ctx, count: int) -> None:
        await ctx.channel.purge(limit=count)
        await ctx.send(f"Deleted `{count}` messages", delete_after=5)
        return

    @staticmethod
    def mode(lis: list):
        n = len(lis)
        data = Counter(lis)
        get_mode = dict(data)
        mode = [k for k, v in get_mode.items() if v == max(list(data.values()))]

        if len(mode) == n:
            return None
        else:
            get_mode = ", ".join(map(str, mode))

        return int(get_mode)

    @commands.command(description="Shows a Pie chart of the servers people activity")
    async def activity(self, ctx) -> None:
        dnd_count = 0
        idle_count = 0
        online_count = 0
        off_count = 0
        for a in ctx.guild.members:
            if a.status == discord.Status.dnd:
                dnd_count += 1
            elif a.status == discord.Status.idle:
                idle_count += 1
            elif a.status == discord.Status.online:
                online_count += 1
            elif a.status == discord.Status.offline:
                off_count += 1
        labels = ["Online", "DND", "Idle", "Offline"]
        sizes = [online_count, dnd_count, idle_count, off_count]
        colors = ["#43b582", "#f04747", "#faa81a", "#747f8d"]
        fig1, ax1 = plt.subplots()
        plt.title(f"{ctx.guild.name} Activity")
        ax1.pie(sizes, shadow=True, startangle=90, colors=colors, labels=labels)
        ax1.axis("equal")
        plt.savefig(f"graphs/{ctx.message.id}_circle.png", transparent=True)
        plt.clf()
        await ctx.send(file=discord.File(f"graphs/{ctx.message.id}_circle.png"))
        return

    @commands.command(description="Know stats of the server")
    async def stats(
        self, ctx, channel_command: Union[discord.TextChannel, discord.Member] = None
    ):
        pass
    """
    @commands.command(description="Know the growth of the server")
    async def joins(self, ctx):
        await ctx.send(':pipenv:')
        joined_date = []
        date_list = []
        count_on_that_day_list = []
        async for member in ctx.guild.fetch_members():
            joined_date.append(member.joined_at.replace(hour=0, minute=0, second=0, microsecond=0))

        dic = {}
        for x in joined_date:
            dic[x] = dic[joined_date.count(x)]

        for x in dic.keys():
            date_list.append(x)
            count_on_that_day_list.append(dic[x])
        date_list, count_on_that_day_list = zip(*sorted(zip(date_list, count_on_that_day_list)))
        plt.xticks(rotation=45)
        plt.plot(list(date_list), list(count_on_that_day_list), color="#87CEEB")
        plt.ylabel("Messages")
        plt.xlabel("Hour")
        plt.savefig(f"graphs/{ctx.message.id}_joins.png", transparent=True)
        plt.clf()
        await ctx.send(file=discord.File(f'graphs/{ctx.message.id}_joins.png'))"""


    @commands.command(description="Know the permission a role has ")
    async def roleinfo(self, ctx, role_id: int) -> None:
        role = ctx.guild.get_role(role_id)
        if role is None:
            return await ctx.send("Role not found. you sure the ID is right?")
        embed = discord.Embed(title=role.name, color=role.color)
        permissions = role.permissions
        stri = ""
        for x, y in iter(permissions):
            if y:
                stri = f"{stri}\n{x}"
        if stri == "":
            stri = "None"

        embed.add_field(name="Permissions", value=stri)
        members_list = []
        for a in role.members:
            members_list.append(a.mention)
        members_stri = "\n".join(members_list)
        if members_stri == "":
            members_stri = "NONE"
        embed.add_field(name="Members in the roles", value=members_stri)
        await ctx.send(embed=embed)
        return

    @commands.command(description="Deletes a value and trigger")
    @commands.has_permissions(kick_members=True)
    async def delreply(self, ctx, word: str = None) -> None:
        if word is None:
            await ctx.send("Tell something that should be removed")
            return
        word = word.lower()
        data = cur.execute(
            f'DELETE FROM reply where SERVER_ID is {ctx.guild.id} AND trigger is "{word}"'
        )
        conn.commit()
        await ctx.send(f'Success now bot don"t care when you say {word}')
        return

    @commands.command(
        description="Tell all the trigger words and there respected reply"
    )
    @commands.has_permissions(kick_members=True)
    async def listreply(self, ctx) -> None:
        cur.execute(
            f"SELECT trigger , value FROM reply where SERVER_ID is {ctx.guild.id}"
        )
        value = cur.fetchall()
        embeds = []
        value = list(sum(value, tuple()))
        for x in range(0, len(value), 2):
            embed = discord.Embed(
                title=value[x], color=0x00FF00, description=value[x + 1]
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
            embeds.append(embed)
        conn.commit()

        if not embeds:
            await ctx.send("Null")
            return

        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()
        return

    @commands.command(description="Tells all the words that ping the role")
    @commands.has_permissions(kick_members=True)
    async def listmodpings(self, ctx) -> None:
        cur.execute(f"SELECT word FROM warn_words where SERVER_ID is {ctx.guild.id}")
        word_list = cur.fetchall()
        word_list = list(sqlconvert(word_list))
        conn.commit()
        cur.execute(f"SELECT mod FROM warn_words where SERVER_ID is {ctx.guild.id}")
        mod_list = cur.fetchall()
        conn.commit()
        mod_list = list(sqlconvert(mod_list))
        temp_list = mod_list
        mod_list = []

        if not word_list:
            word_list = ["None"]

        if not mod_list:
            mod_list = ["None"]

        for a in temp_list:
            mod_list.append(ctx.guild.get_role(a).mention)
        conn.commit()
        embed = discord.Embed(title="Warn_words", color=0x00FF00)
        embed.add_field(name="Word", value="\n".join(word_list))
        embed.add_field(name="Role that get pinged", value="\n".join(mod_list))
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)
        return

    @commands.command(description="INITIATE A REPLYING SETUP")
    @commands.has_permissions(kick_members=True)
    async def reply(self, ctx) -> None:
        def is_correct(m):
            return m.author == ctx.author

        await ctx.send("What should person type ?")
        try:
            message = await self.client.wait_for(
                "message", check=is_correct, timeout=20.0
            )
        except asyncio.TimeoutError:
            return await ctx.send("Sorry, you took too long.")
        trigger = message.content
        trigger = trigger.lower()
        await ctx.send(f"{trigger}  is the trigger")
        await ctx.send("What should bot reply with ?")
        try:
            message = await self.client.wait_for(
                "message", check=is_correct, timeout=20.0
            )
        except asyncio.TimeoutError:
            return await ctx.send("Sorry, you took too long.")
        value = message.content
        value = value.lower()

        embed = discord.Embed(title=trigger, description=value, color=0x00FF00)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        cur.execute(
            f'INSERT INTO reply VALUES("{trigger}" , "{value}" , {ctx.guild.id})'
        )
        conn.commit()
        return

    @commands.command(
        description="INITIATE A SETUP THAT PING A ROLE WHEN A SPECIFIC WORD IS SAID IN GUILD"
    )
    @commands.has_permissions(kick_members=True)
    async def modping(self, ctx) -> None:
        def is_correct(m):
            return m.author == ctx.author

        await ctx.send("What should person type ?")
        try:
            message = await self.client.wait_for(
                "message", check=is_correct, timeout=20.0
            )
        except asyncio.TimeoutError:
            return await ctx.send("Sorry, you took too long.")
        trigger = message.content
        trigger = trigger.lower()
        await ctx.send(f"{trigger} is the trigger")
        await ctx.send("Bot should ping what role ? ID of the role")
        try:
            message = await self.client.wait_for(
                "message", check=is_correct, timeout=20.0
            )
        except asyncio.TimeoutError:
            return await ctx.send("Sorry, you took too long.")
        value = message.content
        value = value.lower()
        try:
            value = int(value)
        except ValueError:
            await ctx.send("I SAID ID")
            return
        try:
            value_ping = ctx.guild.get_role(value)
            value_ping = value_ping.mention
        except:
            await ctx.send("NO ROLE FOUND")
            return
        embed = discord.Embed(title=trigger, description=value_ping, color=0x00FF00)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        cur.execute(
            f'INSERT INTO warn_words values({ctx.guild.id} , "{trigger}" , {value})'
        )
        conn.commit()
        return

    @commands.command(description="Delete a word that ping mods or a role")
    @commands.has_permissions(kick_members=True)
    async def delmodping(self, ctx, word: str) -> None:
        cur.execute(
            f'DELETE FROM warn_words WHERE server_id = {ctx.guild.id} AND word = "{word.lower()}"'
        )
        conn.commit()
        wrod = str(word + " ") * 15
        await ctx.send(f"{word} is no longer block, All hail {wrod}", delete_after=5)
        return

    @commands.command(description="Tells the block words")
    @commands.has_permissions(kick_members=True)
    async def unblock(self, ctx, word: str) -> None:
        cur.execute(
            f'DELETE FROM block WHERE server_id = {ctx.guild.id} AND word = "{word.lower()}"'
        )
        conn.commit()
        wrod = str(word + " ") * 15
        await ctx.send(f"{word} is no longer block, All hail {wrod}", delete_after=5)
        return

    @commands.command(description="Tells the block words")
    @commands.has_permissions(kick_members=True)
    async def blockedwords(self, ctx):
        cur.execute(f"SELECT word FROM block WHERE server_id is {ctx.guild.id}")
        words = cur.fetchall()
        words = list(sum(words, tuple()))
        words = "\n".join(words)
        if words == [""]:
            words = "NONE"

        embed = discord.Embed(
            title="Blocked words", description=str(words), color=0x0000FF
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)

        await ctx.send(embed=embed, delete_after=15)
        return

    @commands.command(description="Blocks a words from the server")
    @commands.has_permissions(kick_members=True)
    async def block(self, ctx, string: str):
        await ctx.message.delete()
        string = string.lower()
        cur.execute(f"SELECT word FROM block WHERE server_id is {ctx.guild.id}")
        conn.commit()
        words = cur.fetchall()
        words = list(sum(words, tuple()))

        if string in words:
            await ctx.send("It is already blocked", delete_after=5)

            return

        cur.execute(f'INSERT INTO block VALUES({ctx.guild.id} , "{string}")')
        conn.commit()
        await ctx.send(
            f'"{string}" is now blocked from the server forever.', delete_after=5
        )
        return

    @commands.command(description="Creates a poll so that people can vote in.")
    @commands.has_permissions(kick_members=True)
    async def poll(self, ctx, question: str, *options: str):
        """Creates a poll"""

        if len(question) > 250:
            return await ctx.send(
                "Question is too long, it can't be more than 250 words"
            )

        for option in options:
            if len(option) > 250:
                return await ctx.send(
                    "Option is too long, it can't be more than 250 words"
                )

        if len(options) <= 1:
            await ctx.send("You need more than one option to make a poll!")
            return
        if len(options) > 10:
            await ctx.send("You cannot make a poll for more than 10 things!")
            return

        if len(options) == 2 and options[0] == "yes" and options[1] == "no":
            reactions = ["\u2705", "\u274c"]
        else:
            reactions = [
                "1\u20e3",
                "2\u20e3",
                "3\u20e3",
                "4\u20e3",
                "5\u20e3",
                "6\u20e3",
                "7\u20e3",
                "8\u20e3",
                "9\u20e3",
                "\U0001f51f",
            ]
        number = 0
        desc = ""
        while number <= len(options) - 1:
            desc += f"{reactions[number]} for {options[number]} \n\n "
            number += 1
        reactions = reactions[: len(options)]
        embed = discord.Embed(title=question, description=desc)
        poll = await ctx.send(embed=embed)
        for a in reactions:
            await poll.add_reaction(a)
        return

    @commands.command(description="Shows infractions of a user")
    async def infractions(self, ctx, person: discord.Member = None) -> None:
        """Shows Infraction of a user"""
        if person is None:
            person = ctx.author
        cur.execute(
            f"select DATE from infractions where SERVER_ID = {ctx.guild.id} AND ID = {person.id}"
        )
        date_list = cur.fetchall()
        date_list = sum(date_list, tuple())
        cur.execute(
            f"select REASON from infractions where SERVER_ID = {ctx.guild.id} AND ID = {person.id}"
        )
        reason_list = cur.fetchall()
        reason_list = sum(reason_list, tuple())
        embed_list = []
        for reason, date in zip(reason_list, date_list):
            embed = discord.Embed(
                title="Your Crimes", description=reason, color=0xFFFFFF
            )
            embed.set_author(name=person.display_name, icon_url=person.avatar_url)
            embed.add_field(name="Dated on", value=date)
            embed_list.append(embed)
        paginator = BotEmbedPaginator(ctx, embed_list)
        try:
            await paginator.run()
        except IndexError:
            return await ctx.send("No infractions good boy.")

    @commands.command(description="Kicks the faggots")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None) -> None:
        """KICKS the faggots xD"""
        reason = f"Kicked by {ctx.author}, for {reason}"
        embed = discord.Embed(
            title=f"You are Kicked from {ctx.guild.name}",
            description=f"Reason - {reason}",
            colour=0x0279FD,
        )
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            print("Failed to DM the warning of kicking/banning")
        await member.kick(reason=reason)
        await ctx.send(f" :thumbsup: KICKED {member}")
        return

    @commands.command(description="Ban the faggots")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban the faggots xD"""
        reason2 = f"Banned by {ctx.author}, for {reason}"
        embed = discord.Embed(
            title=f"You got Banned from {ctx.guild.name}",
            description=f"Reason - {reason}",
            colour=0x0279FD,
        )
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            print("Failed to DM the warning of kicking/banning")

        await member.ban(reason=reason2, delete_message_days=0)
        await ctx.send(f":thumbsup: BANNED! {member}")
        return

    @commands.command(description="Prevent someone from talking in a text channel.")
    @commands.has_permissions(kick_members=True)
    async def mute(
        self, ctx, person: discord.Member, *, reason: str = "No reason given"
    ):
        role_muted = discord.utils.get(ctx.guild.roles, name="Muted")
        if role_muted is None:
            role = await ctx.guild.create_role(name="Muted")
        if role_muted in person.roles:
            await ctx.send(f"**This member is already muted**")
            return
        for role in person.roles:
            try:
                await person.remove_roles(role)
            except discord.Forbidden:
                pass
            except discord.NotFound:
                pass

        await person.add_roles(role_muted)
        embed = discord.Embed(
            title="Muted",
            description=f"Muted {str(person)} for {reason}",
            color=0x00FF00,
        )
        await ctx.send(embed=embed)
        for channel in ctx.guild.channels:
            await channel.set_permissions(
                role,
                send_messages=False,
                read_message_history=False,
                read_messages=None,
                speak=False,
            )
        return

    @commands.command(description="Undo mute command.")
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, person: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if role is None:
            role = await ctx.guild.create_role(name="Muted")
        if role not in person.roles:
            await ctx.send(f"**This member is not muted**")
            return
        await person.remove_roles(role)
        embed = discord.Embed(
            title="Unmuted", description=f"Unmuted {str(person)}", color=0x00FF00
        )
        await ctx.send(embed=embed)
        for channel in ctx.guild.channels:
            await channel.set_permissions(
                role,
                send_messages=False,
                read_message_history=False,
                read_messages=None,
                speak=False,
            )
        return

    @commands.command(description="Warns a person . non removable")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, person: discord.Member, *, reason: str = None) -> None:
        """Warns a person."""
        dateshit = datetime.datetime.now()
        dateshit = f"{dateshit.year} : {dateshit.month} : {dateshit.day}"
        cur.execute(
            f'INSERT INTO infractions VALUES("{dateshit}", {person.id} ,{ctx.guild.id}, "{reason}")'
        )
        # "CREATE TABLE infractions(ID INT(50), SERVER_ID INT(50), REASON VARCHAR(50))")
        conn.commit()

        try:
            embed = discord.Embed(
                title="You have been warned", description=reason, color=0x0279FD
            )
            embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
            await person.send(embed=embed)
        except:
            pass
        await ctx.send(
            f":incoming_envelope: Infraction added to {person.mention} \nReason - {reason}"
        )
        # cur.execute("CREATE TABLE infractions(ID INT(50), REASON VARCHAR(50))")
        return

    print("moderating cog loaded")


def setup(client):
    client.add_cog(Moderating(client))
