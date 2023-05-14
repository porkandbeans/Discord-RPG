import os
import mysql.connector
import json
from dotenv import load_dotenv
import random

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
  items TEXT
);""")
sqlconnect.commit()

# return a JSON object representing the user's inventory
def get_inventory(userid):
    ensure_exists(userid)
    dbcursor.execute("select items from inventories where id=" + str(userid))
    json_string = str(dbcursor.fetchall())[3:-4]
    inventory = json.loads(json_string)
    return inventory

def get_item_by_name(name):
    for i in itemValues["items"]:
        if i["name"].lower() == name.lower():
            return i
    return False

# make sure the user's inventory exists by inserting a row and ignoring errors on duplicat PKs
def ensure_exists(userid):
    dbcursor.execute("SELECT * FROM inventories WHERE id="+str(userid))
    dbcursor.fetchall()
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

    addthis = item

    # item ID 0 is nothing
    if addthis["id"] == 0:
        return

    if "quantity" not in addthis:
        addthis["quantity"] = 1
    # check if the item is stackable
    for ivs in itemValues["items"]:
        if (addthis["id"] == ivs["id"]):
            if not (ivs["stackable"] and search_inventory_for_item(inventory, addthis)):
                inventory["inventory"].append(addthis)
    
    # convert json into valid string data and store in database
    json_str = json.dumps(inventory)
    sql = "UPDATE inventories SET items = %s WHERE id = %s"
    val = (json_str, userid)
    dbcursor.execute(sql, val)
    sqlconnect.commit()

# stack items up if they already exist in the inventory or return false if not found
def search_inventory_for_item(inventory, item):
    for i in inventory["inventory"]:
        if item["id"] == i["id"]:
            #user has this item in their inventory
            if "quantity" not in i:
                i["quantity"] = 1
            if "quantity" not in item:
                item["quantity"] = 1
            i["quantity"] += item["quantity"]
            return True
    
    return False

def surprise_mechanics(userid):
    roll = random.randint(0,10)
    if roll == 0:
        add_to_inventory(userid, json.loads('{"id":3,"quantity":1}'))
        return "You found a **legendary** sword!"
    if roll <= 2:
        roll = random.randint(1,2)
        if roll < 2:
            add_to_inventory(userid, json.loads('{"id":2,"quantity":1}'))
            return "You found an iron sword"
        else:
            add_to_inventory(userid, json.loads('{"id":5,"quantity":1}'))
            return "You found steel armor"
    if roll <= 5:
        coincount = random.randint(10,30)
        add_coins(userid, coincount)
        return "You found " + str(coincount) + " coins."
    if roll > 5:
        if roll < 2:
            add_to_inventory(userid, json.loads('{"id":1,"quantity":1}'))
            return "You found a *shitty* sword. :poop:"
        else:
            add_to_inventory(userid, json.loads('{"id":4,"quantity":1}'))
            return "You found leather armor"
    

#   returns a string detailing the user's current status (AI helped)
def status(userid):
    try:
        dbcursor.execute("SELECT level, coins, weapon, armor, experience_points FROM users WHERE id=" + str(userid))
        result = dbcursor.fetchone()
        if result is None:
            raise ValueError("Result is None")

        weapon = get_item_by_ID(result[2])
        armor = get_item_by_ID(result[3])
        print("Status: " + str(result))
        status_msg = "**Level**: " + str(result[0]) + "\n**Coins**: " + str(result[1]) + "\n**Weapon**: " + weapon["name"] + " (dps: " + str(weapon["dps"]) + ")\n**Armor**: " + armor["name"] + " (defense: " + str(armor["armor"]) + ")\n**Experience Points**: " + str(result[4])
    except mysql.connector.Error as e:
        print(f"MySQL error: {e}")
        return "Error: Could not get user status"
    except ValueError as e:
        print(f"Value error: {e}")
        return "Error: No result for user ID found"

    return status_msg

def add_coins(userid, coins):
    dbcursor.execute("SELECT coins FROM users WHERE id=" + str(userid))
    result = dbcursor.fetchone()
    oldcoins = int(result[0])
    oldcoins += coins
    sql = "UPDATE users SET coins = %s WHERE id = %s"
    val = (str(oldcoins), userid)
    dbcursor.execute(sql, val)
    sqlconnect.commit()
    # return "you now have " + str(oldcoins)
    
#   returns JSON object for item or false if not found
def get_item_by_ID(itemid):
    for ivs in itemValues["items"]:
        if ivs["id"] == itemid:
            return ivs
    return False

#   attempt to equip named item from user's inventory
def equip(userid, item):
    item = item.lower()
    inventory = get_inventory(userid)
    for invitem in inventory["inventory"]:
        i = get_item_by_ID(invitem["id"])
        if item == i["name"].lower():
            if i["is_weapon"]:
                dbcursor.execute("SELECT weapon FROM users WHERE id=" + str(userid))
                result = dbcursor.fetchone()
                equippeditem = get_item_by_ID(result[0])
                add_to_inventory(userid, equippeditem)
                sql = "UPDATE users SET weapon = %s WHERE id= %s"
                vals = (str(i["id"]), str(userid))
                remove_from_inventory(userid, i["id"])
                dbcursor.execute(sql, vals)
                sqlconnect.commit()
                
            if i["is_armor"]:
                dbcursor.execute("SELECT armor FROM users WHERE id=" + str(userid))
                result = dbcursor.fetchone()
                equippeditem = get_item_by_ID(result[0])
                add_to_inventory(userid, equippeditem)
                sql = "UPDATE users SET armor = %s WHERE id= %s"
                vals = (str(i["id"]), str(userid))
                remove_from_inventory(userid, i["id"])
                dbcursor.execute(sql, vals)
                sqlconnect.commit()
            return i["name"] + " equipped."
    
    return "you don't have one of those"

#   removes an item from the user's inventory, or returns false if they don't have one of the item
def remove_from_inventory(userid, itemid):
    item = get_item_by_ID(itemid)
    userinv = get_inventory(userid)

    search_result = search_inventory_for_item(userinv, item)
    if not search_result:
        print("Item not found in inventory")
        return False
    
    for i in userinv["inventory"]:
        if itemid == i["id"]:
            userinv["inventory"].remove(i)
            json_str = json.dumps(userinv)
            sql = "UPDATE inventories SET items = %s WHERE id = %s"
            val = (json_str, userid)
            dbcursor.execute(sql, val)
            sqlconnect.commit()
            print(f"Removed item from inventory: {i}")
            return True

def unequip(userid, type):
    if type != "armor" and type != "weapon":
        return "usage: !rpg unequip weapon, or !rpg unequip armor"
    
    if type == "weapon":
        dbcursor.execute("SELECT weapon FROM users WHERE id=" + str(userid))
        result = dbcursor.fetchone()
        equippeditem = get_item_by_ID(result[0])
        add_to_inventory(userid, equippeditem)
        dbcursor.execute("UPDATE users SET weapon = 0 WHERE id=" + str(userid))
        sqlconnect.commit()
        return "Weapon unequipped, " + str(get_item_by_ID(result[0])["name"]) + " returned to inventory"
    
    if type == "armor":
        dbcursor.execute("SELECT armor FROM users WHERE id=" + str(userid))
        result = dbcursor.fetchone()
        
        equippeditem = get_item_by_ID(result[0])
        print(equippeditem)
        add_to_inventory(userid, equippeditem)
        dbcursor.execute("UPDATE users SET armor = 0 WHERE id=" + str(userid))
        sqlconnect.commit()
        return "Armor unequipped, " + str(get_item_by_ID(result[0])["name"]) + " returned to inventory"

# sell an item from a user's inventory
def sell(userid, item):
    itemobj = get_item_by_name(item.lower())
    if search_inventory_for_item(get_inventory(userid), itemobj) == False:
        return "You don't have one of those."
    remove_from_inventory(userid, itemobj["id"])
    add_coins(userid, itemobj["value"])
    return "Sold " + item + " for " + str(itemobj["value"]) + " coins."

def get_user_weapon(userid):
    dbcursor.execute("SELECT weapon FROM users WHERE id = " + str(userid))
    result = dbcursor.fetchone()
    weapon = get_item_by_ID(result[0])
    return weapon