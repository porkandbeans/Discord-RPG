import os
import discord
from discord.utils import get
from dotenv import load_dotenv
import mysql.connector
import inventory_functions as inv
import monsters as mons

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
  coins INT,
  weapon INT,
  armor INT
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
        (id, name, level, experience_points, coins, weapon, armor)
        VALUES 
        (""" + str(userid) + ", \"" + username + "\", 1, 0, 0, 0, 0)""")
    sqlconnect.commit()

    if (message.content.startswith("!rpg")):
        if (message.content == "!rpg bag"):
            await message.channel.send(str(inv.show_inventory(userid, username)))
            return
        # if (message.content == "!rpg give"):
        #     await message.channel.send(inv.surprise_mechanics(userid))
            return
        if (message.content == "!rpg status"):
            await message.channel.send(inv.status(userid))
            return
        # if (message.content == "!rpg givecoins"):
        #     await message.channel.send(inv.add_coins(userid, 69))
        if (message.content.startswith("!rpg equip ")):
            await message.channel.send(inv.equip(userid, message.content[11:]))
        if (message.content.startswith("!rpg unequip ")):
            await message.channel.send(inv.unequip(userid, message.content[13:]))
        if (message.content.startswith("!rpg sell ")):
            await message.channel.send(inv.sell(userid, message.content[10:]))
        if (message.content == "!rpg spawn"):
            await message.channel.send(mons.spawn_monster(0))
        if (message.content == "!rpg attack"):
            weapon = inv.get_user_weapon(userid)
            result = mons.attack_monster(userid, weapon)
            if type(result) is str:
                await message.channel.send(result)
            elif type(result) is list:
                await message.channel.send("Monster slain!")
                for user in result[1]:
                    await message.channel.send("<@"+str(user)+">")
                    #   dragon slayer role
                    if result[0]["id"] == 4:
                        role = discord.utils.get(message.guild.roles, id=1107217690013224990)
                        await message.author.add_roles(role)
                    for drop in range(0,result[0]["loot-table"]):
                        await message.channel.send(inv.surprise_mechanics(user))
                    await message.channel.send(inv.add_xp(userid, result[0]["XP"]))

    # print(str(userid))


client.run(TOKEN)