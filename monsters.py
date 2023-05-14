import os
import mysql.connector
import json
from dotenv import load_dotenv
import random
from functools import lru_cache

monstertable = json.load(open("monsters.json"))
itemtable = json.load(open("items.json"))
items = itemtable["items"]

load_dotenv()
DB_USER = 'rpgbot'
DB_PASS = os.getenv('DB_PASSWORD')

sqlconnect = mysql.connector.connect(
    host="localhost",
    user=DB_USER,
    password=DB_PASS
)

dbcursor = sqlconnect.cursor()
dbcursor.execute("use discordrpg;")
dbcursor.execute("""
    CREATE TABLE IF NOT EXISTS monster (
        id INT NOT NULL AUTO_INCREMENT,
        monsterid INT,
        hp INT,
        contributors TEXT,
        PRIMARY KEY (id)
    );""")

def get_monster_by_id(id):
    for monster in monstertable["monsters"]:
        if monster["id"] == id:
            return monster
    return False

def spawn_monster(monsterid):
    # make sure there isn't already a monster
    dbcursor.execute("SELECT * FROM monster;")
    dbcursor.fetchall()
    if (dbcursor.rowcount != 0):
        return "There is already a monster!"
    
    if monsterid == 0:
        monsterid = random.randint(1, monstertable["monsters"].count())
        print("no number specified, " + str(monsterid) + " generated.")
    monster = get_monster_by_id(monsterid)
    
    dbcursor.execute("""INSERT INTO monster 
            (monsterid, hp)
            VALUES 
            (""" + str(monster["id"]) + ", " + str(monster["HP"]) + ");")
    sqlconnect.commit()
    
    return monster["name"]

def attack_monster(userid):
    dbcursor.execute("SELECT * FROM monster;")
    dbcursor.fetchall()
    if (dbcursor.rowcount == 0):
        return "There isn't a monster to attack."
    
    dbcursor.execute("SELECT level, coins, weapon, armor, experience_points FROM users WHERE id=" + str(userid))
    result = dbcursor.fetchone()
    print("Result: " + str(result))
    userweapon = get_user_weapon(result[2])
    result = None
    return "Hitting monster for " + str(userweapon["dps"])


def get_user_weapon(id):
    for i in items:
        if i["id"] == id:
            return i
    return False