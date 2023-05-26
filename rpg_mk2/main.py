import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import mysql.connector
import inventory_functions as inv
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DB_USER = 'rpgbot'
DB_PASS = os.getenv('DB_PASSWORD')

sqlconnect = mysql.connector.connect(
    host="localhost",
    user=DB_USER,
    password=DB_PASS
)

dbcursor = sqlconnect.cursor()

dbcursor.execute("create database if not exists discordrpg2;")
dbcursor.execute("use discordrpg2;")
dbcursor.execute("""CREATE TABLE IF NOT EXISTS users (
  id BIGINT PRIMARY KEY,
  name VARCHAR(255),
  level INT,
  experience_points INT,
  coins INT,
  weapon INT,
  armor INT,
  head INT,
  HP INT 
);""")
sqlconnect.commit()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

RUBBISH = 183394842125008896

# show user's inventory
@bot.command()
async def inventory(ctx):
    userid = ctx.author.id
    username = ctx.author.name
    await ctx.channel.send(inv.show_inventory(userid, username))

# show user's status
@bot.command()
async def status(ctx):
    userid = ctx.author.id
    await ctx.channel.send(inv.status(userid))

# debugging command to give an item to userid
@bot.command()
async def drop(ctx):
    userid = ctx.author.id
    if userid != RUBBISH:
        return
    await ctx.channel.send(inv.surprise_mechanics(userid))

@bot.event
async def on_message(message):
    print(message.content)
    username = message.author.name
    userid = message.author.id
    messagecontent = message.content.lower()

    # create an entry in the database for a user if one does not already exist
    # if an entry already exists for a user, it throws a duplicate entry error (which is ignored)
    dbcursor.execute("""INSERT IGNORE INTO users 
        (id, name, level, experience_points, coins, weapon, armor, head, HP)
        VALUES 
        (""" + str(userid) + ", \"" + username + "\", 1, 0, 0, 0, 0, 0, 100)""")
    sqlconnect.commit()
    
    if random.randint(0,100) == 1:
        await message.channel.send("You found a drop!")
        await message.channel.send(inv.surprise_mechanics(userid))

    inv.add_xp(userid, 10)

    # process commands, thanks clyde
    await bot.process_commands(message)

    return

bot.run(TOKEN)