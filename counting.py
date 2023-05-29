import os
import discord
import mysql.connector
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('COUNTING_TOKEN')
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
dbcursor.execute("CREATE TABLE IF NOT EXISTS counting (id INT PRIMARY KEY, number BIGINT, userid BIGINT);")

# execute a SELECT query to check if the row exists
dbcursor.execute("SELECT * FROM counting WHERE id=0")
row = dbcursor.fetchone()

# if the row exists, print a message, otherwise print an error message
if row is not None:
    print("Existing row found, not inserting")
else:
    dbcursor.execute("INSERT INTO counting (id, number, userid) VALUES (0, 1, 0);")


COUNTING_CHANNEL = 1051261584556699738

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_message(message):
    channel = message.channel
    userid = message.author.id
    dbcursor.execute("SELECT number, userid FROM counting WHERE id=0")
    fetch = dbcursor.fetchone()
    current_number = int(fetch[0])
    db_userid = int(fetch[1])
    if channel.id != COUNTING_CHANNEL:
        return
    
    if message.author.id == 1106463817669558344:
        return
    
    # buttsbot
    if message.author.id == 1111148610042732584:
        return
    
    # RPGbot
    if message.author.id == 1105988701642821722:
        return

    words = message.content.split()
    
    if words[0].isdigit():
        number = int(words[0])
    else:
        # first word was NaN
        await message.channel.send("YA FUCKED IT UP! start over from 1.")
        dbcursor.execute("UPDATE counting SET number=1, userid=0")
        return

    if number != current_number:
        # number was not the right number
        await message.channel.send("YA FUCKED IT UP! start over from 1.")
        dbcursor.execute("UPDATE counting SET number=1, userid=0")
        return
    
    if message.author.id == db_userid:
        # no cutting in line
        await message.channel.send("WAIT YOUR TURN! start over from 1.")
        dbcursor.execute("UPDATE counting SET number=1, userid=0")
        return

    # update the number
    current_number += 1
    dbcursor.execute("UPDATE counting SET number=%s, userid=%s where id=0", (current_number, userid))

    sqlconnect.commit()

client.run(TOKEN)