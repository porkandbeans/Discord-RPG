import os
import discord
import mysql.connector
from discord.utils import get
from dotenv import load_dotenv

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

dbcursor.execute("create database if not exists counting;")
dbcursor.execute("use counting;")
dbcursor.execute("CREATE TABLE IF NOT EXISTS counting (id INT PRIMARY KEY, number BIGINT);")
dbcursor.execute("INSERT INTO counting (id, number) VALUES (0, 1);")

COUNTING_CHANNEL = 1051261584556699738

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_message(message):
    channel = message.channel
    dbcursor.execute("SELECT number FROM counting WHERE id=0")
    fetch = dbcursor.fetchone()
    current_number = fetch[0]
    if channel.id != COUNTING_CHANNEL:
        return
    
    if message.author.id == 1105988701642821722:
        return

    try:
        number = int(message.content)
        if number == current_number:
            current_number += 1
            dbcursor.execute("UPDATE counting SET number=" + str(current_number))
        else:
            await message.channel.send("YA FUCKED IT UP! start over from 1.")
            dbcursor.execute("UPDATE counting SET number=1")
    except ValueError:
        await message.channel.send("YA FUCKED IT UP! start over from 1.")
        dbcursor.execute("UPDATE counting SET number=1")

    sqlconnect.commit()

client.run(TOKEN)