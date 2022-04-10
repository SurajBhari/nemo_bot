from difflib import SequenceMatcher
import nekos
from gtts import gTTS
import sqlite3
import discord
from discord.ext import commands
import datetime
import random
import asyncio
from typing import Union
import aiohttp
import async_cse
import html
import json
import re
import sr_api
import textwrap
from pyfiglet import Figlet
from utils.multiple_choice import BotMultipleChoice
from utils.pagination import BotEmbedPaginator
from utils.confirmation import BotConfirmation
from copy import deepcopy
import aiosqlite
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import numpy as np
from data.config import lemonoji_mapping

import async_cleverbot as ac

sr_client = sr_api.Client()

conn = sqlite3.connect("data.db")
cur = conn.cursor()

color = "white"
plt.rcParams.update({"font.size": 13})
plt.rcParams.update({"text.color": color, "axes.labelcolor": color})
plt.rcParams["text.color"] = color
plt.rcParams["axes.labelcolor"] = color
plt.rcParams["xtick.color"] = color
plt.rcParams["ytick.color"] = color


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.g_client_token = 'AIzaSyCFMDFE1TRGQoo9rf8hdzuLQ-VwAMQ29eM'
        self.g_client = async_cse.Search(self.g_client_token)
        self.cb_token = 'QOXOzM9qcm/wGZ_rkAD['
        self.emotion = ac.Emotion.neutral
        self.edited_snipe = {}
        self.snipe = {}

    """
    @commands.command(description='do some bullshit')
    async def textt(self, ctx):
        await ctx.send('Nice that you are here . say a word i will suggest a picture from google if you think that'
                       'picture tells about the word then react to it. doing it for word guessing game'
                       'Type `abort` if you wanna exit.')
        while True:
            with open('/home/ag/my_bot/guessing_word.json', "r+") as f:
                data = json.load(fp=f)

            def is_correct(m):
                return m.author == ctx.author and m.channel.id == ctx.channel.id

            try:
                message = await self.client.wait_for(
                    "message", check=is_correct, timeout=10.0
                )
            except asyncio.TimeoutError:
                return await ctx.send("Sorry, you took too long.")

            if message.content.lower() == 'abort':
                await ctx.send('K bye :) Thanks for contributing.')
                return

            results = await self.g_client.search(message.content, safesearch=True, image_search=True)
            result = results[0]
            embed = discord.Embed(
                title=result.title,
                url=result.url,
                description=result.description,
                color=0x00FF00,
            )
            embed.set_image(url=result.image_url)

            await ctx.send(embed=embed)

            confirmation = BotConfirmation(ctx, 0x0000FF)
            await confirmation.confirm(
                f"Does this picture describes {message.content} ?"
            )
            if confirmation.confirmed:
                await confirmation.update("Confirmed", color=0x55FF55)
                data[message.content] = result.image_url
                open('/home/ag/my_bot/guessing_word.json', 'w+').close()
                with open('/home/ag/my_bot/guessing_word.json', "w") as f:
                    json.dump(data, f, sort_keys=True, indent=4)

                await ctx.send('Added.')
            else:
                await confirmation.update("Not confirmed", hide_author=True, color=0xFF5555)"""

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None and message.author.id != self.client.user.id:
            async with message.author.typing():
                cleverbot = ac.Cleverbot(self.cb_token)
                cleverbot.set_context(ac.DictContext(cleverbot))
                response = await cleverbot.ask(
                    message.content, message.author.id, emotion=self.emotion
                )
                await message.author.send(response.text)
                await cleverbot.close()

            embed = discord.Embed(
                title="New DM", description=message.content, color=0x00FF00
            )
            embed.add_field(name="Reply", value=response.text)
            embed.set_author(
                name=message.author.name, icon_url=message.author.avatar_url
            )
            server = self.client.get_guild(820450746776289281)
            channel = server.get_channel(854201290104111136)
            await channel.send(embed=embed)
        

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        try:
            self.snipe[str(message.guild.id)]
        except KeyError:
            self.snipe[str(message.guild.id)] = []
        self.snipe[str(message.guild.id)].append(message)

    @commands.command(description="Snipe a deleted message")
    async def snipe(self, ctx):
        try:
            x = self.snipe[str(ctx.guild.id)]
        except KeyError:
            await ctx.send('No message logged here', delete_after=7.5)
            return
        x = x[::-1]
        try:
            y = x[0]
        except IndexError:
            await ctx.send('No message logged here', delete_after=7.5)
            return
        embeds_list = []
        for result in x:
            embed = discord.Embed(
                title=f'Sniped a message from {str(result.author)} in {result.channel.name}',
                description=result.content,
                color=0x00FF00,
            )
            if len(result.attachments) != 0 or result.attachments is not None:
                try:
                    embed.set_image(url=result.attachments[0].proxy_url)
                except IndexError:
                    pass
            embed.set_author(name=result.author.name, icon_url=result.author.avatar_url)
            embed.timestamp = result.created_at
            embeds_list.append(embed)

        paginator = BotEmbedPaginator(ctx, embeds_list)
        await paginator.run()

    @commands.command(description="Change emotion of the bot")
    @commands.is_owner()
    async def emotion(self, ctx, *, emotion: int = None):
        if emotion is None:
            await ctx.send(
                f"1 for neutral\n"
                f"2 for sad\n"
                f"3 for fear\n"
                f"4 for joy\n"
                f"5 for anger\n"
                f"Current Emotion is {self.emotion}"
            )
            return
        if emotion == 1:
            self.emotion = ac.Emotion.neutral
        elif emotion == 2:
            self.emotion = ac.Emotion.sad
        elif emotion == 3:
            self.emotion = ac.Emotion.fear
        elif emotion == 4:
            self.emotion = ac.Emotion.joy
        elif emotion == 5:
            self.emotion = ac.Emotion.anger
        await ctx.send(f"Set mood to \n{self.emotion}")
        return

    @commands.command(description="Google Search")
    async def google(self, ctx, *, search: str):
        if ctx.channel.is_nsfw():
            safe_search = False
        else:
            safe_search = True
        results = await self.g_client.search(search, safesearch=safe_search)
        embeds_list = []
        for result in results:
            embed = discord.Embed(
                title=result.title,
                url=result.url,
                description=result.description,
                color=0x00FF00,
            )
            embeds_list.append(embed)

        paginator = BotEmbedPaginator(ctx, embeds_list)
        await paginator.run()
        return

    @commands.command(description="Google Image Search")
    async def image(self, ctx, *, search: str):
        if ctx.channel.is_nsfw():
            safe_search = False
        else:
            safe_search = True

        results = await self.g_client.search(
            search, safesearch=safe_search, image_search=True
        )
        embeds_list = []
        for result in results:
            embed = discord.Embed(
                title=result.title,
                url=result.url,
                description=result.description,
                color=0x00FF00,
            )
            embed.set_image(url=result.image_url)
            embeds_list.append(embed)
            embed.set_footer(text=f'Safe search - {safe_search}')

        paginator = BotEmbedPaginator(ctx, embeds_list)
        await paginator.run()
        return

    @commands.command(description="Just try it and see!")
    async def figlet(self, ctx, *, words: str):

        f = Figlet(font="slant")
        thingy = f.renderText(words)

        thingy = f"Make sure to see from a desktop client to understand easily \n```\n{thingy}\n```"
        if len(thingy) > 2000:
            await ctx.send("Too much text to figgle please use less things.")
            return
        await ctx.send(thingy)
        return

    @commands.command(
        description="Figlet but its random font , remember it may crash sometime"
    )
    async def figletran(self, ctx, *, words: str):
        with open("fonts.txt", "r") as f:
            fonts = f.readlines()
        choice = random.choice(fonts)
        font = choice[:-1]

        f = Figlet(font=font)
        thingy = f.renderText(words)

        thingy = (
            f"Make sure to see from a desktop client to understand easily. \n"
            f"If the command return something weird please use figlet command as that one is stabler than "
            f"this one. \n font - {font} \n```\n{thingy}\n```"
        )
        if len(thingy) > 2000:
            await ctx.send("Too much text to figgle please use less things.")
            return
        await ctx.send(thingy)
        return

    @commands.command(description="Make a story from the chat.")
    async def compile(self, ctx, channel: discord.TextChannel = None, limit: int = 500):
        if channel is None:
            channel = ctx.channel
        message = await ctx.send("Processing. this can take some while")
        messages = await channel.history(limit=limit).flatten()

        text = ""
        content = []
        for xyz in messages:
            if not xyz.author.bot:
                content.append(xyz.content)

        if len('\n----'.join(content)) > 950:
            embeds = []
            xz = '```'
            for part in content:
                if len(xz) < 1000 and len(xz + part + '\n' + '- ') < 1000:
                    xz = xz + '- ' + discord.utils.escape_markdown(part) + '\n'
                else:
                    xz = xz + '```'
                    embed = discord.Embed(title=channel.name, color=0x00FF00, )
                    embed.add_field(name="Content", value=xz)
                    embeds.append(embed)
                    xz = '```'
            paginator = BotEmbedPaginator(ctx, embeds)
            await paginator.run()
            return
        else:
            embed = discord.Embed(title=channel.name, color=0x00FF00)
            embed.add_field(name="Content", value=text)
            await ctx.send(embed=embed)
            return

    @commands.command(description="Memes for the win")
    async def meme(self, ctx):
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, "http://meme-api.herokuapp.com/gimme")
            string = html
            data = json.loads(string)

            imagestart = json.dumps(data["url"])
            image = imagestart.replace('"', "")

            # title
            titlestart = json.dumps(data["title"])
            title = titlestart.replace('"', "")

            # Subreddit
            substart = json.dumps(data["subreddit"])
            sub = substart.replace('"', "")

            # post
            poststart = json.dumps(data["postLink"])
            post = poststart.replace('"', "")

            tmsg = "[{}]({})".format(title, post)
            bmsg = ", Subreddit: r/{}".format(sub)

            embed = discord.Embed(
                title="", timestamp=datetime.datetime.utcnow(), color=0x00FFFF
            )
            embed.add_field(name="Have a meme!", value=(tmsg))
            embed.set_image(url=(image))
            embed.set_footer(
                text=ctx.message.author.name + f"{bmsg}", icon_url=ctx.author.avatar_url
            )
            await ctx.send(embed=embed)
            return

    @commands.command(description="Hug someone fo you")
    async def hug(self, ctx, person: discord.User = None) -> None:
        """Hug someone you like"""

        if person is None or person == ctx.author:
            await ctx.send("Mention someone to hug you can't hug yourself :C sadly")
            return

        embed = discord.Embed(
            title="Hugging!",
            description=f"{ctx.author.mention} hugged {person.mention}",
            color=0x9B59B6,
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        link = await sr_client.get_gif("hug")
        link = link.url
        embed.set_image(url=str(link))

        data = cur.execute(
            f"INSERT INTO hugs VALUES({ctx.author.id} , {person.id} , {ctx.guild.id})"
        )
        conn.commit()
        await ctx.send(embed=embed)
        return

    @commands.command(description="Tells your hugs")
    async def hugs(self, ctx, person: discord.User = None) -> None:
        """How many people hugged you ?"""
        if person is None:
            person = ctx.author

        data = cur.execute(
            f"SELECT COUNT(hugger_id) FROM hugs where hugged_person = {person.id}"
        )
        text = cur.fetchone()
        text = str(text)
        text = text.replace(")", "")
        text = text.replace("(", "")
        text = text.replace(",", "")
        embed = discord.Embed(
            title=f"{person.name} have been hugged", description=f"{text} times", colour=0x9B59B6
        )
        embed.set_author(name=person.name, icon_url=person.avatar_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_thumbnail(
            url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/237/hugging-face_1f917.png"
        )
        await ctx.send(embed=embed)
        return

    @commands.command(description="Find out how much someone loves you.")
    async def love(self, ctx, person: discord.Member):
        percent = random.randrange(0, 100)
        embed = discord.Embed(
            title=f"{percent}% :heart:",
            description=f"{ctx.author.mention} Loves {person.mention} at the rate of {percent}%",
            color=0xFF00FF,
        )
        await ctx.send(embed=embed)
        return

    @commands.command(description="Returns a random anime quote")
    async def quote(self, ctx) -> None:
        quote = await sr_client.anime_quote()

        embed = discord.Embed(
            title=quote.character, color=0x00FFFF, description=quote.anime
        )
        embed.add_field(name="Quote", value=quote.quote)
        await ctx.send(embed=embed)
        return

    @staticmethod
    def similar(a: str, b: str) -> int:
        return int(float(SequenceMatcher(None, a, b).ratio()) * 100)

    @commands.command(description="Test your typing speed")
    async def typingtest(self, ctx: commands.context) -> None:
        paragraphs = []
        with open("paragraph.txt", "r") as file:
            for a in file.readlines():
                paragraphs.append(a)

        choosen_word = random.choice(paragraphs)
        choosen_word = choosen_word.lower()

        fake_word = ""
        for letter in choosen_word:
            fake_word = fake_word + "⁣" + letter

        await ctx.send(f"Your sentence is \n`{fake_word}`")
        start_time = datetime.datetime.utcnow()

        def is_correct(m):
            return m.author == ctx.author

        while True:
            try:
                message = await self.client.wait_for(
                    "message", check=is_correct, timeout=520.0
                )
            except asyncio.TimeoutError:
                return
            if "⁣" in message.content:
                await ctx.send("You fricking cheater.\n"
                               "Bye.")
                return

            else:
                similarity = self.similar(a=message.content.lower(), b=choosen_word.lower())
                if similarity > 90:
                    end_time = datetime.datetime.utcnow()
                    seconds = int((end_time - start_time).total_seconds())
                    await ctx.send(
                        f"GG \nIt took you {seconds} seconds\n"
                        f'WPM = {int(len(choosen_word.split(" ")) / (seconds / 60))} \n'
                        f'Similarity = {similarity}%'
                    )
                    return

    @commands.command(description="Ask you some questions")
    async def trivia(self, ctx: commands.context, category: int = None) -> None:
        choice = ""
        if category is None:
            async with aiohttp.ClientSession() as session:
                html1 = await fetch(session, "https://opentdb.com/api_category.php")
                data = json.loads(html1)
                for a in data["trivia_categories"]:
                    choice = f'{choice}\n{a["id"]}. {a["name"]}'
                embed = discord.Embed(
                    title="Make a choice and type it in the chat.",
                    color=0x00FFFF,
                    description=choice,
                )
                await ctx.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                msg = await ctx.send("Choose one!")
                try:
                    message = await self.client.wait_for(
                        "message", check=check, timeout=20.0
                    )
                except asyncio.TimeoutError:
                    return
                try:
                    content = int(message.content)
                except ValueError:
                    await ctx.send("That doesn't look like a number! Retry from starting.")
                    return
                if content not in range(9, 33):
                    await ctx.send("You really think that is a valid ID ? Retry")
                    return
                category = content

        async with aiohttp.ClientSession() as session:
            html1 = await fetch(
                session,
                f"https://opentdb.com/api.php?amount=1&category={category}&type=multiple",
            )
            data = json.loads(html1)
            try:
                options = [
                    html.unescape(data["results"][0]["correct_answer"]),
                    html.unescape(data["results"][0]["incorrect_answers"][0]),
                    html.unescape(data["results"][0]["incorrect_answers"][1]),
                    html.unescape(data["results"][0]["incorrect_answers"][2]),
                ]
                answer = options[0]
                question = html.unescape(data["results"][0]["question"])
            except IndexError:
                pass
            options = sorted(options, key=lambda x: random.random())
            multiple_choice = BotMultipleChoice(ctx, options, f"{question}")
            await multiple_choice.run()
            await multiple_choice.quit(multiple_choice.choice)
            user_answer = multiple_choice.choice
            if user_answer.lower() == data["results"][0]["correct_answer"].lower():
                embed = discord.Embed(title="Correct!", color=0x0000FF, )
                embed.add_field(name=question, value=answer)
                embed.set_image(
                    url="https://media1.tenor.com/images/bcb961b67dc5ec34381372494c85c8fe/tenor.gif"
                )
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            else:
                embed = discord.Embed(
                    title="Wrong!",
                    color=0xFF0000,
                    description=f"Correct answer was {data['results'][0]['correct_answer']}",
                )
                embed.add_field(name=question, value=answer)
                embed.set_image(
                    url="https://media1.tenor.com/images/44ce8109895aa2070c7aa70ca1d51504/tenor.gif"
                )
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=embed)

    @commands.command(description="Wink someone for you")
    async def wink(self, ctx, person: discord.User = None) -> None:
        """kiss someone you like"""

        if person is None:
            await ctx.send(
                "Mention someone to Wink you can't wink at yourself :C sadly"
            )
            return

        embed = discord.Embed(
            title="Winking!",
            description=f"{ctx.author.mention} Winked at {person.mention}",
            color=0x9B59B6,
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        link = await sr_client.get_gif("wink")
        link = link.url
        embed.set_image(url=str(link))
        data = cur.execute(
            f"INSERT INTO winks VALUES({ctx.author.id} , {person.id} , {ctx.guild.id})"
        )
        conn.commit()
        await ctx.send(embed=embed)
        return

    @commands.command(description="Tells your Winks")
    async def winks(self, ctx, person: discord.User = None) -> None:
        """How many people winked at you ?"""
        if person is None:
            person = ctx.author

        data = cur.execute(
            f"SELECT COUNT(winker_id) FROM winks where winked_person = {person.id}"
        )
        text = cur.fetchone()
        text = str(text)
        text = text.replace(")", "")
        text = text.replace("(", "")
        text = text.replace(",", "")
        embed = discord.Embed(
            title="You have been winked at",
            description=f"{text} times",
            colour=0x9B59B6,
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_thumbnail(
            url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/237/winking-face_1f609.png"
        )
        await ctx.send(embed=embed)
        return

    @commands.command(description="Echo whatever you say")
    @commands.has_permissions(kick_members=True)
    async def echo(self, ctx, *, what_to_be_echoed) -> None:
        """Echo whatever you say"""
        await ctx.send(what_to_be_echoed)
        await ctx.message.delete()
        return

    @commands.command(description="Generate a random no. from 2 args given.")
    async def randomnumber(self, ctx, a: int, b: int) -> None:
        """Generate a random no. from 2 args given."""
        x = random.randrange(a, b)
        print(x)
        await ctx.send(f"Random no. generated is \n{x}")
        return

    @commands.command(description="Tells an random fun fact")
    async def fact(self, ctx) -> None:

        facts_list = []
        f = open("facts.txt", "r+")
        for a in f.readlines():
            facts_list.append(a)
        choosen_one = random.choice(facts_list)
        await ctx.send(choosen_one)
        return

    @commands.command(description="You don't like someone ? use this ")
    async def roast(self, ctx, person_to_roast: discord.Member) -> None:
        """You don't like someone ? use this """
        roast_list = []
        f = open("roasts.txt", "r+")
        for a in f.readlines():
            roast_list.append(a)
        choosen_one = random.choice(roast_list)
        choosen_one = f"{person_to_roast.mention}, {choosen_one}--{ctx.author.mention}"
        await ctx.send(choosen_one)
        return

    @commands.command(
        description="Gives a .mp3 file saying what you have given in the args"
    )
    async def say(self, ctx, *, words: str = "Give something to be spoken.") -> None:
        """Gives a .mp3 file saying what you have given in the args"""
        ctx.message.content = words
        words = ctx.message.clean_content

        tts = gTTS(words)
        try:
            tts.save("output.mp3")
        except AssertionError:
            await ctx.send("You need to type better words. This is not supported.")
            return

        await ctx.send(
            content="here what you asked for :)", file=discord.File("output.mp3")
        )
        return

    @commands.command(description="Toses a coin")
    async def toss(self, ctx) -> None:
        """Toses a coin"""

        message = await ctx.send("FLIPPING A COIN! ")
        final = random.choice(["Heads", "Tails"])
        if final == "Heads":
            await ctx.send(content="Its a Heads", file=discord.File("head.png"))
        elif final == "Tails":
            await ctx.send(content="Its a Tails", file=discord.File("tails.png"))
        return

    @commands.command(description="Same as say, but in reverse")
    async def sayre(self, ctx, *, words: str = "Give something to be spoken.") -> None:
        """Same as say, but in reverse"""

        def reverse(x):
            return x[::-1]

        ctx.message.content = words
        words = ctx.message.clean_content

        words = reverse(words)
        tts = gTTS(words)
        try:
            tts.save("output.mp3")
        except AssertionError:
            await ctx.send("You need to type better words. This is not supported.")
            return
        thingy = reverse("here what you asked for :)")

        await ctx.send(content=thingy, file=discord.File("output.mp3"))
        return

    @commands.command(description="For when you wanna settle the score some other way")
    async def choose(self, ctx, *choices: str) -> None:
        """Chooses between multiple choices."""
        await ctx.send(random.choice(choices))
        return

    @commands.command(description="Says if a user is cool")
    async def cool(self, ctx, user: discord.Member) -> None:
        """Says if a user is cool."""

        if user != self.client:
            await ctx.send(f"No {user.mention} is not cool")
        return

    @commands.command(description="Know usage of a character over the internet.")
    async def charusage(self, ctx, char: str = None):
        with open("/home/ag/my_bot/charusage.json", "r+") as f:
            data = json.load(fp=f)

        if char is not None:
            if len(char) > 1:
                await ctx.send(f'> Wanted only one character, example of command can be `{ctx.prefix}charusage s`')
                return
            try:
                count = data[char]
            except IndexError:
                count = 0
            await ctx.send(embed=discord.Embed(title=char, description=f'```\n{count}```', color=0x00ff00))
            return
        objects = []
        count = []
        for entry in data.keys():
            objects.append(entry)
            count.append(data[entry])
        count, objects = zip(*sorted(zip(count, objects), reverse=True))
        count = count[:20]
        objects = objects[:20]
        y_pos = np.arange(len(objects))
        plt.bar(y_pos, count, align="center", alpha=0.5)
        plt.xticks(y_pos, objects)
        plt.ylabel("Usage")
        plt.title("Character usage")
        plt.savefig(f"graphs/{ctx.message.id}_char.png", transparent=True)
        plt.clf()
        await ctx.send(file=discord.File(f"graphs/{ctx.message.id}_char.png"))
        await ctx.send("Raw File", file=discord.File('charusage.json'))
        return

    """
    @commands.command(description="Know usage of a word over the internet.")
    async def wordusage(self, ctx, word: str = None):
        with open("/home/ag/my_bot/wordusage.json", "r+") as f:
            data = 'x'
            stri = f.readlines()
            stri = ''.join(stri)
            for x in range(10):  # 10 tries
                try:
                    data = json.loads(re.escape(stri))
                except Exception as e:
                    if x < 2:
                        await ctx.send(f'Error \n{e} ')
                    pass
                else:
                    break
            if data == 'x':
                await ctx.send('Hmmm. seems like a error is encountered you can try again in 2 minutes')
                return

        if word is not None:
            try:
                count = data[word]
            except KeyError:
                count = 0
            await ctx.send(embed=discord.Embed(title=word, description=f'```\n{count}```', color=0x00ff00))
            return
        objects = []
        count = []
        for entry in data.keys():
            objects.append(entry)
            count.append(data[entry])
        embed_list = []

        count, objects = zip(*sorted(zip(count, objects), reverse=True))
        count = count[:500]
        objects = objects[:500]
        for x in range(int(len(count) / 10)):
            desc = "```css\nCharacter - Usage count\n"
            for y in range(1, 11):
                try:
                    desc = f"{desc}{objects[x + y]} - {count[x + y]}\n"
                except IndexError:
                    desc = desc
            desc = desc + "```"
            embed = discord.Embed(title="Word usage", description=desc, color=0x00FF00)
            embed_list.append(embed)
        await ctx.send("Raw File", file=discord.File('wordusage.json'))
        paginator = BotEmbedPaginator(ctx, embed_list)
        await paginator.run()
        return 
    """

    @commands.command(description="Raise a given number to given power")
    async def power(
            self, ctx: commands.Context, number: float, power: float = 1
    ) -> None:
        if number > 1000000000000000 or power > 1000000000000:
            await ctx.send("Go easy on me ")
            return

        answer = number ** power

        if len(str(answer)) > 2000:
            await ctx.send("Number too big to send")
        else:
            await ctx.send(answer)

        return

    @commands.command(
        name="bookmark",
        aliases=["bm"],
        description="Send you a direct link of a message to your DM.",
    )
    async def bookmark(
            self,
            ctx: commands.Context,
            target_message: discord.Message = None,
            *,
            title: str = "Bookmark",
    ) -> None:
        """Send the author a link to `target_message` via DMs. If Nothing is provided it take the commanding message."""
        if target_message is None:
            target_message = ctx.message

        # Prevent users from bookmarking a message in a channel they don't have access to
        permissions = ctx.author.permissions_in(target_message.channel)
        if not permissions.read_messages:
            embed = discord.Embed(
                title="Nope",
                color=0xFF0000,
                description="You don't have permission to view this channel.",
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=title, colour=0x00FF00, description=target_message.content
        )
        embed.add_field(
            name="Wanna give it a visit?",
            value=f"[Visit original message]({target_message.jump_url})",
        )
        embed.set_author(
            name=target_message.author, icon_url=target_message.author.avatar_url
        )
        embed.set_thumbnail(
            url="https://images-ext-2.discordapp.net/external"
                "/zl4oDwcmxUILY7sD9ZWE2fU5R7n6QcxEmPYSE5eddbg/"
                "%3Fv%3D1/https/cdn.discordapp.com/emojis/654080405988966419.png?width=20&height=20"
        )

        error_embed = discord.Embed(
            title="Nope",
            description=f"Please enable DMs to receive the bookmark. "
                        f"Once done you can retry by reacting with \U0001f4cc",
            colour=0xFF0000,
        )
        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(embed=error_embed, delete_after=7.5)
            sent_person = set()
        else:
            await ctx.message.add_reaction("\U0001F4E8")
            sent_person = {ctx.author}  # set of id who got the message

        await ctx.message.add_reaction("\U0001f4cc")

        copied_embed = deepcopy(embed)

        copied_embed.add_field(
            name=f"Bookmarked from {ctx.author.name}.",
            value=f"[Visit original message]({ctx.message.jump_url})",
            inline=False,
        )

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return (
                    user != self.client.user
                    and reaction.emoji == "\U0001f4cc"
                    and reaction.message == ctx.message
                    and user not in sent_person
            )

        while True:
            try:
                reaction, user = await self.client.wait_for(
                    "reaction_add", timeout=60.0, check=check
                )
            except asyncio.TimeoutError:
                try:
                    await ctx.message.clear_reactions()
                except discord.Forbidden:
                    pass
                return

            try:
                if user == ctx.author:
                    await user.send(embed=embed)
                else:
                    await user.send(embed=copied_embed)

            except discord.Forbidden:
                await ctx.send(
                    f"{user.mention} Please enable your DM to receive the message.",
                    delete_after=7.5,
                )
                await reaction.remove(user)
            except discord.HTTPException:
                await reaction.remove(user)
            else:
                sent_person.add(user)

    @commands.command(description="Why?")
    async def why(self, ctx) -> None:
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, "https://nekos.life/api/v2/why")
            data = json.loads(html)
            await ctx.send(embed=discord.Embed(title=data["why"]))
            return

    @commands.command(description="OwOfy text")
    async def owo(self, ctx, *, text: str) -> None:
        await ctx.send(nekos.owoify(text))
        return

    @commands.command(description="textcatify")
    async def textcat(self, ctx) -> None:
        await ctx.send(nekos.textcat())
        return

    @commands.command(description="returns a cute cat picture or sometime gif.")
    async def cat(self, ctx) -> None:
        await ctx.send(embed=discord.Embed(color=0xFF69B4).set_image(url=nekos.cat()))
        return

    @commands.command(
        name="8ball", description="Let 8 ball answer your question and your faith"
    )
    async def eightball(self, ctx, *, text: str) -> None:
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, "https://nekos.life/api/v2/8ball")
            data = json.loads(html)
            embed = discord.Embed(title=data["response"], color=0x00FF00)
            embed.set_image(url=data["url"])
            await ctx.send(embed=embed)
            return

    @commands.command(description="Hacks People")
    async def hack(self, ctx, person=None) -> None:
        """Hack you."""
        if person is None:
            await ctx.send("> You have to tag someone to make it work.")
            return
        hack_terms = [
            "Got Epic Games Login \nUser - SexsayBitch6969 \nPass-Fuck me hard baby",
            "Deploying multi viruses",
            "Got access to browser history",
            "Found Porn in History",
            "Deploying a back door",
            "Hack status 90%",
            "Blowing up the processor",
            "Downloading RAM",
            "bypassing fortnite anti cheat",
            "minecraft aimbot injected",
            "purchasing winrar",
            "forced all editors into light mode",
            "stealing your bitcoins",
            "lowering KDA in CoD",
            "forcing screen resolution to lock at 640x480 using windows 95 theme",
        ]
        m = await ctx.send(f"Hacking {person}")
        for a in range(7):
            await asyncio.sleep(1)
            await m.edit(content=random.choice(hack_terms))
        await m.edit(
            content="Hacking complete left behind 6969 viruses and 420 Backdoors."
        )
        await ctx.send(f"Done hacking {person}")
        return

    print("Fun cog loaded")


def setup(client):
    client.add_cog(Fun(client))
