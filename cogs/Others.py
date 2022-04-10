import discord
from discord.ext import commands
from utils.multiple_choice import BotMultipleChoice
from utils.pagination import BotEmbedPaginator
from utils.confirmation import BotConfirmation
import json
import random


class Others(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.hidden_cog = ["CommandErrorHandler", "main", "Jishaku", "SQL"]

    @commands.command(description="Returns a invite link from which you can invite me.")
    async def invite(self, ctx):
        embed = discord.Embed(
            title="Click here",
            url="https://discordapp.com/oauth2/authorize?client_id=361810062894956555"
                "&scope=bot&permissions=8",
            color=0x0000ff
        )
        await ctx.send(embed=embed)
        return

    @commands.command(description="Tells about The bot", aliases=['info'])
    async def about(self, ctx):
        embed = discord.Embed(
            title="Who am I ?",
            description="It all started with a project for a streamer to make a giveaway bot that only rolls the winner"
            " when he put the command instead of a timer. The bot was named `Simple Giveaway Bot`. But as "
            "time passed My creator decided to make me. In the end the Giveaway Bot was merged in me. ",
            color=0x00FFFF,
        )
        with open("/home/ag/my_bot/commandusage.json", "r+") as f:
            data = json.load(fp=f)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        ag = self.client.get_user(408994955147870208)  # my Id
        embed.add_field(name="My Creator", value=str(ag))
        embed.add_field(
            name="Invite link, I am still in development keep that in mind",
            value=f"[Click Here!](https://discordapp.com/oauth2/authorize?client_id={self.client.user.id}"
            "&scope=bot&permissions=8) ",
        )
        embed.add_field(name="Commands Count", value=str(len(self.client.commands)))
        embed.add_field(name="Cogs/Category Count", value=str(len(self.client.cogs)))
        embed.add_field(name="Command Usage", value=str(len(data.keys())))

        await ctx.send(embed=embed)

    @commands.command(description="Ping of the bot.")
    async def ping(self, ctx):
        await ctx.send(f"{int(self.client.latency * 1000)}ms")

    @commands.command(description="Servers I am in")
    async def servers(self, ctx):
        await ctx.send(f"I am in `{len(self.client.guilds)}` servers")

    @staticmethod
    def progress_bar(self, a: int, b: int) -> str:
        filled = self.client.get_emoji(710205770452697169)
        string = ""
        empty = self.client.get_emoji(710205770519805982)
        percentage = int((a/b)*100)
        out_of_10 = int(round(percentage / 10))
        string = f'{(str(filled) * out_of_10) + (str(empty) * (10 - out_of_10)) } {str(a)}/{str(b)}'
        return string

    @commands.command(description="Returns a blacked out version of percentage out of 2 given arg")
    async def progress(self, ctx, a: int, b: int):
        await ctx.send(self.progress_bar(self, a=a, b=b))

    @commands.command(description="Help command but all command are shown at once")
    async def help2(self, ctx):
        embed = discord.Embed(title="Helpong", color=0x00ff00)
        for x in self.client.cogs:
            xyz = ", ".join([f"`{y.name}`" for y in self.client.get_cog(x).get_commands()])
            if not xyz:
                xyz = "None"
            if x not in self.hidden_cog:
                embed.add_field(name=x, value=xyz, inline=False)
        await ctx.send(embed=embed)

    @commands.command(descritpion="Help command but it is default help command")
    async def help3(self,ctx, command:str= None):
        if command is None:
            await ctx.send_help()
            return
        else:
            command = self.client.get_command(command)
            if command is None:
                await ctx.send('No command found with that name.')
                return
            await ctx.send_help(command)
            return

    print("Other cog loaded")


def setup(client):
    client.add_cog(Others(client))
