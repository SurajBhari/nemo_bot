from discord.ext import commands
import sr_api
import aiohttp
from typing import Union
import discord
from datetime import datetime

sr_client = sr_api.Client()


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


class Steam(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.key = "29A9DB5F5BEF253A5AFBCB1D9D1CEA58"

    @commands.command(description="Get steam profile info from url")
    async def steaminfo(self, ctx, steam_id: Union[str, int]):
        if type(steam_id) == str:
            steam_id = steam_id.replace("/", "")
            steam_id = steam_id.replace("\\", "")
            steam_id = steam_id[-17:]
            try:
                steam_id = int(steam_id)
            except ValueError:
                await ctx.send(
                    "That doesn't looks like a valid steam id \n"
                    "A valid steam id link looks like "
                    "`https://steamcommunity.com/profiles/76561198438348309/`"
                )
                return
        base_url = (
            "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/"
            f"v0002/?key={self.key}&steamids={steam_id}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as r:
                res = await r.json()  # returns dict
                base = res["response"]["players"][0]
                try:
                    realname = base["realname"]
                except KeyError:
                    realname = "Unknown"
                embed = discord.Embed(
                    title=base["personaname"],
                    url=base["profileurl"],
                    description=realname,
                    color=0xBAB8B6,
                )
                state = base["personastate"]
                if state == 0:
                    state = "Offline"
                elif state == 1:
                    state = "Online"
                elif state == 2:
                    state = "Busy"
                elif state == 3:
                    state = "Away"
                elif state == 4:
                    state = "Snooze"
                elif state == 5:
                    state = "Looking to trade"
                elif state == 6:
                    state = "Looking to play"
                else:
                    state = "Unknown"
                visibility = base["communityvisibilitystate"]
                if visibility == 1:
                    visibility = "Private"
                elif visibility == 3:
                    visibility = "Public"
                else:
                    visibility = "Unknown"
                embed.set_thumbnail(url=base["avatarfull"])
                try:
                    embed.add_field(
                        name="Time Created",
                        value=f'{datetime.utcfromtimestamp(base["timecreated"])} UTC',
                    )
                except KeyError:
                    pass
                try:
                    embed.add_field(
                        name="Last log off",
                        value=f'{datetime.utcfromtimestamp(base["lastlogoff"])} UTC',
                    )
                except KeyError:
                    embed.add_field(name="Last log off", value=f"Unknown")
                embed.add_field(name="State", value=state)
                embed.add_field(name="Visibility", value=visibility)

        base_url = (
            "http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/"
            f"?key={self.key}&steamid={steam_id}&format=json"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as r:
                res = await r.json()  # returns dict
                if res["response"] == {}:
                    embed.add_field(name="Recent game played count", value="Unknown")
                else:
                    base = res["response"]["games"]
                    try:
                        embed.add_field(
                            name="Recent game played count",
                            value=res["response"]["total_count"],
                        )
                    except KeyError:
                        pass
                    for game in base:
                        desc = (
                            f'Previous 2 week playtime - {int(game["playtime_2weeks"]/60)} hr \n'
                            f'Total Hours - {int(game["playtime_forever"]/60)} hr \n'
                        )
                        try:
                            embed.add_field(name=game["name"], value=desc, inline=False)
                        except KeyError:
                            pass

        base_url = (
            "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
            f"?key={self.key}&steamid={steam_id}&format=json"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as r:
                res = await r.json()  # returns dict
                if res["response"] == {}:

                    embed.add_field(name="Recent game played count", value="Unknown")
                else:
                    base = res["response"]["games"]
                    try:
                        embed.add_field(
                            name="Games owned.",
                            value=res["response"]["game_count"],
                            inline=False,
                        )
                    except KeyError:
                        pass

        base_url = (
            "http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/"
            f"?key={self.key}&steamids={steam_id}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as r:
                res = await r.json()  # returns dict
                base = res["players"][0]
                desc = (
                    f'Community Banned - {base["CommunityBanned"]} \n'
                    f'VAC Banned - {base["VACBanned"]} \n'
                    f'Economy Banned - {base["EconomyBan"]} \n'
                )
                embed.add_field(name="VAC status", value=desc, inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Steam(client))
