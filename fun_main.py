from discord.ext import commands
import sqlite3
import os
import datetime
from data.config import token
import discord


async def get_pre(client, message):
    if not message.guild:
        return commands.when_mentioned_or(">")(client, message)
    cur.execute(f"select prefix from prefixes where guild_id is {message.guild.id}")
    prefix = cur.fetchall()
    prefix = list(sum(prefix, tuple()))
    try:
        prefix = prefix[0]
    except IndexError:
        prefix = ">"
    conn.commit()
    return commands.when_mentioned_or(prefix)(client, message)

intents = discord.Intents.all()

description = """Fun Just Fun """
client = commands.Bot(
    command_prefix=get_pre, description=description, case_insensitive=True, intents=intents, owner_ids = [408994955147870208, 715060442627702875]
)
conn = sqlite3.connect("data.db")
cur = conn.cursor()


try:
    cur.execute("CREATE TABLE prefixes(prefix VARCHAR, guild_id INT(50)) ")
    conn.commit()
except sqlite3.OperationalError:
    print("prefixes Table already exist")

try:
    cur.execute(
        "CREATE TABLE reaction(guild_id INT(50), role_id INT(50), message_id INT(50), channel_id INT(50), "
        "reaction VARCHAR(50)) "
    )
    conn.commit()
except sqlite3.OperationalError:
    print("reaction Table already exist")
try:
    cur.execute(
        "CREATE TABLE livedata(guild_id INT(50), channel INT(50), role INT(50), link VARCHAR, last VARCHAR, "
        "message VARCHAR) "
    )
    conn.commit()
except sqlite3.OperationalError:
    print("livedata Table already exist")

try:
    cur.execute("CREATE TABLE ui_temp(user ID(50), message_id ID(50))")
    conn.commit()
except sqlite3.OperationalError:
    print("Ui_temp Table already exist")

try:
    cur.execute("CREATE TABLE log(guild_id INT(50), channel_id INT(50))")
    conn.commit()
except sqlite3.OperationalError:
    print("log Table already exist")

try:
    cur.execute(
        "CREATE TABLE GIVEAWAY(time INT(50), guild_id INT(50), channel_id INT(50), message_id INT(50), item VARCHAR("
        "50))"
    )
    conn.commit()
except sqlite3.OperationalError:
    print("Giveaway Table already exist")

try:
    cur.execute(
        "CREATE TABLE infractions(DATE VARCHAR(50), ID INT(50), SERVER_ID INT(50), REASON VARCHAR(50))"
    )
    conn.commit()
except sqlite3.OperationalError:
    print("Table infractions already exist")

try:
    cur.execute("CREATE TABLE desc(ID INT(50), desc VARCHAR(50))")
    conn.commit()
except sqlite3.OperationalError:
    print("Table infractions already exist")

try:
    cur.execute("CREATE TABLE reply(trigger VARCHAR, value VARCHAR, SERVER_ID INT(50))")
    conn.commit()
except sqlite3.OperationalError:
    print("Table reply already exist")

try:
    cur.execute(
        "CREATE TABLE hugs(hugger_id ID(50), hugged_person INT(50), SERVER_ID INT(50))"
    )
    conn.commit()
except sqlite3.OperationalError:
    print("Table huggers already exist")

try:
    cur.execute(
        "CREATE TABLE winks(winker_id ID(50), winked_person INT(50), SERVER_ID INT(50))"
    )
    conn.commit()
except sqlite3.OperationalError:
    print("Table winks already exist")

try:
    cur.execute("CREATE TABLE block(server_id ID(50), word VARCHAR )")
    conn.commit()
except sqlite3.OperationalError:
    print("Table block already exist")

try:
    cur.execute("CREATE TABLE blacklisted(server_id ID(50), person_id ID(50) )")
    conn.commit()
except sqlite3.OperationalError:
    print("Table blacklisted already exist")

try:
    cur.execute("CREATE TABLE warn_words(server_id ID(50), word VARCHAR , mod INT(50))")
    conn.commit()
except sqlite3.OperationalError:
    print("Table warn_words already exist")

try:
    cur.execute(
        "CREATE TABLE ticket(guild_id ID(50), log ID(50) , role ID(50), category ID(50))"
    )
    conn.commit()
except sqlite3.OperationalError:
    print("Table ticket already exist")


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

client.load_extension("jishaku")


@client.command(description="Disables a bot command")
@commands.is_owner()
async def disable(ctx, command_name: str):
    cmd = client.get_command(command_name.lower())
    if cmd is None:
        return await ctx.send("Command not found duhh")
    cmd.enabled = False
    return await ctx.send(f"Done disabled {cmd.name}")


@client.command(description="Enables a bot command")
@commands.is_owner()
async def enable(ctx, command_name: str):
    cmd = client.get_command(command_name.lower())
    if cmd is None:
        return await ctx.send("Command not found duhh")
    cmd.enabled = True
    return await ctx.send(f"Done Enabled {cmd.name}")


@client.command(description="Tells disabled commands")
async def disabled(ctx):
    disabled_command = "\n".join([str(x.name) for x in client.commands if not x.enabled])
    if not disabled_command:
        disabled_command = "None"
    await ctx.send(disabled_command)


def Humanize(date:datetime.datetime):
    return date.strftime('%a %d %b %y, %H:%M:%S')


client.Humanize = Humanize


@client.event
async def on_ready():
    cur.execute(f"select person_id from blacklisted")
    list_ = cur.fetchall()
    list_ = list(sum(list_, tuple()))
    client.blacklist = list_
    conn.commit()


@client.check
def check_commands(ctx):
    cur.execute(f"select person_id from blacklisted")
    list_ = cur.fetchall()
    list_ = list(sum(list_, tuple()))
    client.blacklist = list_
    conn.commit()
    client.blacklist = list_
    return ctx.author.id not in list_


client.run(token)
