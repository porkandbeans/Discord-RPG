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
        monsterid = random.randint(1, len(monstertable["monsters"]) - 1)
        print("no number specified, " + str(monsterid) + " generated.")
    monster = get_monster_by_id(monsterid)
    
    dbcursor.execute("""INSERT INTO monster 
            (monsterid, hp)
            VALUES 
            (""" + str(monster["id"]) + ", " + str(monster["HP"]) + ");")
    sqlconnect.commit()
    
    return monster["name"]

def attack_monster(userid, weapon):
    dbcursor.execute("SELECT * FROM monster;")
    result = dbcursor.fetchone()
    if (result == None):
        return "There isn't a monster to attack."
    
    print(str(result[0]))
    monster = get_monster_by_id(result[1])

    if result[3] == None:
        contributors = []
    else:
        contributors = json.loads(result[3])
    
    if weapon == False:
        weapon = {"dps": 1}
    
    monsterhp = result[2] - weapon["dps"]

    if userid not in contributors:
        contributors.append(userid)

    query = """
        UPDATE monster
        SET HP = %s, contributors = %s
        WHERE id = %s
    """

    values = (monsterhp, json.dumps(contributors), result[0])

    dbcursor.execute(query, values)
    sqlconnect.commit()

    returnstring = "Hitting " + monster["name"] + " for " + str(weapon["dps"]) + " - " + str(monster["name"]) + " has " + str(monsterhp) + " HP remaining."

    if monsterhp <= 0:
        returnstring += "\n" + monster["name"] + " has been slain!"
        dbcursor.execute("DELETE FROM monster WHERE id=" + str(result[0]))
        sqlconnect.commit()
        return contributors
    return returnstring