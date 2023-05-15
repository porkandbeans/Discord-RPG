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
  armor INT,
  HP INT
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
        (id, name, level, experience_points, coins, weapon, armor, HP)
        VALUES 
        (""" + str(userid) + ", \"" + username + "\", 1, 0, 0, 0, 0, 100)""")
    sqlconnect.commit()

    content = message.content.lower()
    if (not content.startswith("!rpg")):
        return

    if not inv.check_player_alive(userid):
        await message.channel.send("You are dead and must wait to be revived.")
        return

    if (content == "!rpg bag"):
        await message.channel.send(str(inv.show_inventory(userid, username)))
        return
    if (content == "!rpg status"):
        await message.channel.send(inv.status(userid))
        return
    
    #   user string inputs, scary danger zone
    if (content.startswith("!rpg equip ")):
        await message.channel.send(inv.equip(userid, content[11:]))
    if (content.startswith("!rpg unequip ")):
        await message.channel.send(inv.unequip(userid, content[13:]))
    if (content.startswith("!rpg sell ")):
        await message.channel.send(inv.sell(userid, content[10:]))
    if (content.startswith("!rpg use ")):
        await message.channel.send(inv.use_item(userid, content[9:])["string"])
    if (content.startswith("!rpg revive <@")):
        await message.channel.send(inv.revive_player(userid, content[14:-1]))

    if (content == "!rpg spawn"):
        await message.channel.send(mons.spawn_monster(0))
    if (content == "!rpg attack"):
        weapon = inv.get_user_weapon(userid)
        result = mons.attack_monster(userid, weapon)
        
        if result["status"] == "no monster":
            await message.channel.send("There are no monsters to fight.")
            return

        if result["status"] == "fighting":
            await message.channel.send(result["string"])
            await message.channel.send(inv.take_damage(userid, result["damage"])["string"])
        else:
            await message.channel.send("Monster slain!")
            for user in result["contributors"]:
                await message.channel.send("<@"+str(user)+">")
                #   dragon slayer role
                if result["monster"]["id"] == 4:
                    role = discord.utils.get(message.guild.roles, id=1107217690013224990)
                    await message.author.add_roles(role)
                for drop in range(0,result["monster"]["loot-table"]):
                    await message.channel.send(inv.surprise_mechanics(user))
                await message.channel.send(inv.add_xp(userid, result["monster"]["XP"]))
        

    # print(str(userid))


client.run(TOKEN)