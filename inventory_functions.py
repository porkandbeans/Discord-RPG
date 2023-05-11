import os
import mysql.connector
import json
from dotenv import load_dotenv

itemValues = json.load(open("items.json"))

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
dbcursor.execute("""CREATE TABLE IF NOT EXISTS inventories (
  id BIGINT PRIMARY KEY,
  items VARCHAR(255)
);""")
sqlconnect.commit()

# return a JSON object representing the user's inventory
def get_inventory(userid):
    ensure_exists(userid)
    dbcursor.execute("select items from inventories where id=" + str(userid))
    json_string = str(dbcursor.fetchall())[3:-4]
    inventory = json.loads(json_string)
    return inventory

# make sure the user's inventory exists by inserting a row and ignoring errors on duplicat PKs
def ensure_exists(userid):
    dbcursor.execute("SELECT * FROM inventories where id="+str(userid))
    dbcursor.fetchall()
    print(dbcursor.fetchall())
    if (dbcursor.rowcount == 0):
        dbcursor.execute("""INSERT INTO inventories 
            (id, items)
            VALUES 
            (""" + str(userid) + ", '{\"inventory\": []}');")
        sqlconnect.commit()
        

# returns the user's inventory row
def show_inventory(userid, username):
    inventory = get_inventory(userid)

    returnvalue = "Inventory for " + username + ": \n"
    if len(inventory["inventory"]) > 0:
        for item in inventory["inventory"]:
            for ivs in itemValues["items"]:
                if item["id"] == ivs["id"]:
                    returnvalue += "- " + ivs["name"] + "(" + str(item["quantity"]) + ")\n"
    else:
        returnvalue += "nothing"

    return returnvalue


# add an item to a user's inventory
def add_to_inventory(userid, item):
    inventory = get_inventory(userid)
    addthis = json.loads(item)

    # check if the item is stackable
    for ivs in itemValues["items"]:
        if addthis["id"] == ivs["id"]:
            if ivs["stackable"]:
                search_inventory_for_item(inventory, addthis)
            else:
                inventory["inventory"].append(addthis)
    
    # convert json into valid string data and store in database
    json_str = json.dumps(inventory)
    sql = "UPDATE inventories SET items = %s WHERE id = %s"
    val = (json_str, userid)
    dbcursor.execute(sql, val)
    sqlconnect.commit()

# stack items up if they already exist in the inventory
def search_inventory_for_item(inventory, item):
    for i in inventory["inventory"]:
        if item["id"] == i["id"]:
            #user has this item in their inventory
            i["quantity"] += item["quantity"]
            return