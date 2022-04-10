import discord
from discord.ext import commands
import asyncio
import sqlite3

conn = sqlite3.connect("data.db")
cur = conn.cursor()


class ReactionRole(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.client.get_guild(payload.guild_id)
        if guild is None:
            return
        try:

            cur.execute(
                f'select role_id from reaction where guild_id is {payload.guild_id} and message_id is {payload.message_id} and reaction = "{str(payload.emoji)}"'
            )
            result = cur.fetchall()
            conn.commit()
            result = list(sum(result, tuple()))
            temp_list = result
            result = []
            for a in temp_list:
                guild = self.client.get_guild(payload.guild_id)
                role = guild.get_role(a)
                result.append(role)
                user = guild.get_member(payload.user_id)
            for a in result:
                await user.add_roles(a)
            channel = guild.get_channel(payload.channel_id)
            try:
                await user.send(
                    f"{user.mention} you got the {role.name} !", delete_after=7.5
                )
            except discord.Forbidden:
                try:
                    await channel.send(
                        f"{user.mention} you got the {role.name} !", delete_after=7.5
                    )
                except discord.Forbidden:
                    pass

        except UnboundLocalError:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.client.get_guild(payload.guild_id)
        if guild is None:
            return
        try:

            cur.execute(
                f"select role_id from reaction where guild_id is {payload.guild_id} and message_id is"
                f' {payload.message_id} and reaction = "{str(payload.emoji)}"'
            )
            result = cur.fetchall()
            conn.commit()
            result = list(sum(result, tuple()))
            temp_list = result
            result = []
            for a in temp_list:
                guild = self.client.get_guild(payload.guild_id)
                role = guild.get_role(a)
                result.append(role)
                user = guild.get_member(payload.user_id)
            for a in result:
                await user.remove_roles(a)
            channel = guild.get_channel(payload.channel_id)
            try:
                await user.send(
                    f"{user.mention} you lost the {role.name} !", delete_after=7.5
                )
            except discord.Forbidden:
                try:
                    await channel.send(
                        f"{user.mention} you lost the {role.name} !", delete_after=7.5
                    )
                except discord.Forbidden:
                    pass

        except UnboundLocalError:
            pass

    @commands.command(description="List all the reaction role for the server.")
    async def rrlist(self, ctx):
        # "CREATE TABLE reaction(guild_id INT(50), role_id INT(50), message_id INT(50), reaction VARCHAR(50)) ")

        cur.execute(f"select role_id from reaction where guild_id = {ctx.guild.id}")
        role_id_list = cur.fetchall()
        role_id_list = list(sum(role_id_list, tuple()))
        temp_list = role_id_list
        role_id_list = []
        for x in temp_list:
            role = ctx.guild.get_role(x)
            role_id_list.append(role.mention)
        conn.commit()

        cur.execute(f"select message_id from reaction where guild_id = {ctx.guild.id}")
        message_id_list = cur.fetchall()
        conn.commit()
        message_id_list = list(sum(message_id_list, tuple()))
        cur.execute(f"select channel_id from reaction where guild_id = {ctx.guild.id}")
        channel_id_list = cur.fetchall()
        conn.commit()
        channel_id_list = list(sum(channel_id_list, tuple()))
        temp_list = channel_id_list
        channel_id_list = []
        for a in temp_list:
            channel = ctx.guild.get_channel(a)
            channel_id_list.append(channel.mention)

        cur.execute(f"select reaction from reaction where guild_id = {ctx.guild.id}")
        reaction_id_list = cur.fetchall()
        conn.commit()
        reaction_id_list = list(sum(reaction_id_list, tuple()))

        desc = ""
        for message, channel, emoji, role in zip(
            message_id_list, channel_id_list, reaction_id_list, role_id_list
        ):
            desc = desc + "\n" + f"{channel} | {emoji} | {role} | {message} |"
        embed = discord.Embed(title=ctx.guild.name, description=desc, color=0xFFFF00)
        await ctx.send(embed=embed)
        return

    @commands.command(description="Delete a reaction role from message id. ")
    @commands.has_permissions(kick_members=True)
    async def rrdel(self, ctx, id: int):
        cur.execute(
            f"delete from reaction where guild_id = {ctx.guild.id} and message_id = {id}"
        )
        conn.commit()
        await ctx.send("Done if there was one,")
        return

    @commands.command(description="Initialize adding process")
    @commands.has_permissions(kick_members=True)
    async def rradd(self, ctx):
        def is_correct(m):
            return m.author == ctx.author

        msg = await ctx.send("First of all **ID** of the channel where message is.")
        try:
            message = await self.client.wait_for(
                "message", check=is_correct, timeout=20.0
            )
        except asyncio.TimeoutError:
            return await ctx.send("Sorry, you took too long.")

        channel_id = int(message.content)
        channel = ctx.guild.get_channel(channel_id)
        if channel is None:
            await ctx.send("Could'nt Find the channel please do it again.")
            return
        await message.delete()

        await msg.edit(content="Now **ID** of the message from the channel you told us")
        try:
            message = await self.client.wait_for(
                "message", check=is_correct, timeout=20.0
            )
        except asyncio.TimeoutError:
            return await ctx.send("Sorry, you took too long.")
        message_id = int(message.content)
        await message.delete()
        try:
            target_message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send("Message not found")
            return

        await msg.edit(content="Now react with the Emoji you want to this message")

        def is_correct_2(reaction, user):
            return user == message.author

        try:
            reaction = await self.client.wait_for(
                "reaction_add", check=is_correct_2, timeout=20.0
            )
        except asyncio.TimeoutError:
            return await ctx.send("Sorry, you took too long.")

        await msg.edit(content="Finally the **ID** of the role you want to give.")
        reaction = list(reaction)
        reaction = reaction[0]

        try:
            role = await self.client.wait_for("message", check=is_correct, timeout=20.0)
        except asyncio.TimeoutError:
            return await ctx.send("Sorry, you took too long.")
        role_id = int(role.content)
        await role.delete()
        role = ctx.guild.get_role(role_id)
        if role is None:
            await ctx.send("Role not found . try again")
            return

        embed = discord.Embed(
            title="Succesful",
            description="Congrats its a ~~boy~~ success ",
            color=0x00FF00,
        )
        await msg.delete()
        embed.add_field(name="Reaction", value=reaction)
        embed.add_field(name="Channel", value=channel.mention)
        embed.add_field(name="Role", value=role.mention)
        embed.add_field(name="Message", value=f"[here]({target_message.jump_url})")

        try:
            await target_message.add_reaction(str(reaction))
        except discord.Forbidden:
            await ctx.send(
                "I am not allowed to add reaction to the message you specified"
            )
            return
        await ctx.send(embed=embed)
        hash2 = str(reaction.emoji)
        cur.execute(
            f"insert into reaction values({ctx.guild.id}, {role_id}, {target_message.id},"
            f' {channel_id}, "{hash2}")'
        )
        conn.commit()
        return


def setup(client):
    client.add_cog(ReactionRole(client))
    print("Reaction role cog loaded")
