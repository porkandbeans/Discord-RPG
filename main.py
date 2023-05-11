import os
import discord
from discord.utils import get
from dotenv import load_dotenv
import mysql.connector
import inventory_functions as inv

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

dbcursor.execute("create database if not exists discordrpg;")
dbcursor.execute("use discordrpg;")
dbcursor.execute("""CREATE TABLE IF NOT EXISTS users (
  id BIGINT PRIMARY KEY,
  name VARCHAR(255),
  level INT,
  experience_points INT,
  coins INT
);""")
sqlconnect.commit()

# my personal Discord user ID
RUBBISH = 183394842125008896

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_message(message):
    username = message.author.name
    userid = message.author.id

    # create an entry in the database for a user if one does not already exist
    # if an entry already exists for a user, it throws a duplicate entry error (which is ignored)
    dbcursor.execute("""INSERT IGNORE INTO users 
        (id, name, level, experience_points, coins)
        VALUES 
        (""" + str(userid) + ", \"" + username + "\", 1, 0, 0)""")
    sqlconnect.commit()


    if (message.content.startswith("!rpg")):
      if (message.content == "!rpg show"):
          await message.channel.send(str(inv.show_inventory(userid, username)))
          return
      if (message.content == "!rpg give"):
          inv.add_to_inventory(userid, '{"id":0,"quantity":1}')
    # print(str(userid))


client.run(TOKEN)