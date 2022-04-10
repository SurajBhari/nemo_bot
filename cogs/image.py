import json
import discord
import requests
from discord.ext import commands
from PIL import Image, ImageOps
import sr_api
import random
import aiohttp
from typing import Union
import asyncdagpi


sr_client = sr_api.Client()


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


class Images(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.nasa_key = 'XEwMZgfzNx4SYcsApkQ2nTcw4C59QURCQ0C779Xp'


    @commands.command(description="Astronomy Picture of the Day")
    async def apod(
        self, ctx,
    ):
        async with aiohttp.ClientSession() as session:
            html = await fetch(
                session,
                "https://api.nasa.gov/planetary/apod?api_key"
                f"={self.nasa_key}",
            )
            data = json.loads(html)
            embed = discord.Embed(
                title=data["title"], description=data["explanation"], color=0x0000FF
            )
            embed.set_image(url=data["hdurl"])
            embed.set_footer(text=data["date"])
            await ctx.send(embed=embed)

    @commands.command(description="Random Space Picture.")
    async def nasa(
        self, ctx,
    ):
        random_no = random.randint(1, 99)
        async with aiohttp.ClientSession() as session:
            html = await fetch(
                session, "https://images-api.nasa.gov/search?media_type=image"
            )
            data = json.loads(html)
            embed = discord.Embed(
                title=data["collection"]["items"][random_no]["data"][0]["title"],
                description=data["collection"]["items"][random_no]["data"][0][
                    "description"
                ],
                color=0x0000FF,
            )
            embed.set_image(
                url=data["collection"]["items"][random_no]["links"][0]["href"]
            )
            embed.set_footer(
                text=data["collection"]["items"][random_no]["data"][0]["date_created"]
            )
            await ctx.send(embed=embed)

    @commands.command(description="Random Earth Picture.")
    async def earth(
        self, ctx,
    ):
        random_no = random.randint(1, 1381)
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, "https://epic.gsfc.nasa.gov/api/natural/all")
            data = json.loads(html)
            date = data[random_no]["date"]
            html = await fetch(
                session, f"https://epic.gsfc.nasa.gov/api/natural/date/{date}"
            )
            data = json.loads(html)
            random_no = random.randint(1, 10)
            caption = data[random_no]["caption"]
            image = data[random_no]["image"]
            date = data[random_no]["date"]
            url_date = date[:-9]
            url_date = url_date.replace("-", "/")
            embed = discord.Embed(title=caption, color=0x0000FF)
            embed.set_image(
                url=f"https://epic.gsfc.nasa.gov/archive/natural/{url_date}/jpg/{image}.jpg"
            )
            embed.set_footer(text=date)
            await ctx.send(embed=embed)

    @commands.command(description='Get Random Pics from rovers. Using NASA"s API.')
    async def mars(
        self, ctx,
    ):

        available = [
            "NAVCAM",
            "FHAZ",
        ]
        chosen = random.choice(available)
        random_no = random.randint(0, 9)
        if chosen == available[1]:
            random_no = random.randint(0, 1)

        async with aiohttp.ClientSession() as session:
            html = await fetch(
                session,
                "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000"
                f"&api_key={self.nasa_key}&camera={chosen}",
            )
            data = json.loads(html)
            embed = discord.Embed(title=data["photos"][random_no]["rover"]["name"])
            embed.set_image(url=data["photos"][random_no]["img_src"])
            embed.set_footer(text=data["photos"][random_no]["earth_date"])
            await ctx.send(embed=embed)

    @commands.command(description="Black & Whites your profile picture.")
    async def blackandwhite(self, ctx, person: discord.Member = None):
        """Black and whites your profile picture"""
        if person is None:
            person = ctx.author

        avatar = person.avatar_url_as(format="png", size=1024)
        print(avatar)

        r = requests.get(avatar)

        with open("./bw.png", "wb") as f:
            f.write(r.content)

        im = Image.open("./bw.png").convert("RGB")
        im_invert = ImageOps.grayscale(im)
        im_invert.save("./bw.png")

        await ctx.send(file=discord.File("bw.png"))

    @commands.command(description="Rotates your profile picture.")
    async def rotate(self, ctx, person: discord.Member = None, angle: int = 180):
        """Rotate's your picture"""
        if person is None:
            person = ctx.author
        if angle is None:
            if person is None:
                person = ctx.author

        avatar = person.avatar_url_as(format="png", size=1024)
        print(avatar)

        r = requests.get(avatar)

        with open("./rotated.png", "wb") as f:
            f.write(r.content)

        im = Image.open("./rotated.png").convert("RGB")
        im_rotate = im.rotate(angle=angle)
        im_rotate.save("./rotated.png")

        await ctx.send(file=discord.File("rotated.png"))

    @commands.command(description="Flips your profile picture Top to bottom.")
    async def flip1(self, ctx, person: discord.Member = None):
        """Flip's your picture Top to bottom."""
        if person is None:
            person = ctx.author

        avatar = person.avatar_url_as(format="png", size=1024)
        print(avatar)

        r = requests.get(avatar)

        with open("./flipped.png", "wb") as f:
            f.write(r.content)

        im = Image.open("./flipped.png").convert("RGB")
        im_rotate = im.transpose(method=Image.FLIP_TOP_BOTTOM)
        im_rotate.save("./flipped.png")

        await ctx.send(file=discord.File("flipped.png"))

    @commands.command(description="Flips your profile picture sideways.")
    async def flip2(self, ctx, person: discord.Member = None):
        """Flip's sideways your picture"""
        if person is None:
            person = ctx.author

        avatar = person.avatar_url_as(format="png", size=1024)
        print(avatar)

        r = requests.get(avatar)

        with open("./flipped.png", "wb") as f:
            f.write(r.content)

        im = Image.open("./flipped.png").convert("RGB")
        im_flipped = im.transpose(method=Image.FLIP_LEFT_RIGHT)
        im_flipped.save("./flipped.png")

        await ctx.send(file=discord.File("flipped.png"))


print("Images cog loaded")


def setup(client):
    client.add_cog(Images(client))
