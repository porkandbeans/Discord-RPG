import os
import discord
from discord.utils import get
from dotenv import load_dotenv
import mysql.connector

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

dbcursor.execute("create database if not exists aichat;")
dbcursor.execute("use aichat;")

client = discord.Client(intents=discord.Intents.all())
@client.event
async def on_message(message):
    channelid = message.channel.id
    authorid = message.author.id
    content = message.content

    dbcursor.execute(f"SHOW TABLES LIKE '{channelid}'")
    result = dbcursor.fetchone()

    if not result:
        # Create a new table for this channel ID
        dbcursor.execute("CREATE TABLE `" + str(channelid) + "` (id INT AUTO_INCREMENT PRIMARY KEY, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, author TEXT, message TEXT)")

        # Commit the changes to the database
        sqlconnect.commit()
    
    query = "insert into `"+str(channelid)+"` (author, message) values (%s, %s);"
    vals = (authorid, content)
    dbcursor.execute(query, vals)
    sqlconnect.commit()
    
client.run(TOKEN)