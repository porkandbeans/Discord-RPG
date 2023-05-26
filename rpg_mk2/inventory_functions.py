import os
import mysql.connector
import json
from dotenv import load_dotenv
import random

itemValues = json.load(open("items.json"))

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
dbcursor.execute("use discordrpg2;")
dbcursor.execute("""CREATE TABLE IF NOT EXISTS inventories (
  id BIGINT PRIMARY KEY,
  items TEXT
);""")
sqlconnect.commit()

# return a JSON object representing the user's inventory
def get_inventory(userid):
    ensure_exists(userid)
    dbcursor.execute("SELECT items FROM inventories WHERE id = %s", (userid,))
    result = dbcursor.fetchone()
    json_string = result[0] if result is not None else "{}"
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
                    if(item["quantity"] > 1):
                        returnvalue += "> " + ivs["name"] + " (" + str(item["quantity"]) + ")\n"
                    else:
                        returnvalue += "> " + ivs["name"] + "\n"
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
    if addthis["stackable"]:
        existingobject = search_inventory_for_item(inventory, addthis)
        if existingobject != False:
            addthis["quantity"] += existingobject["quantity"]
            replace_item_in_inventory(inventory, addthis)
        else:
            inventory["inventory"].append(addthis)
    else:
        inventory["inventory"].append(addthis)

    # convert json into valid string data and store in database
    json_str = json.dumps(inventory)
    sql = "UPDATE inventories SET items = %s WHERE id = %s"
    val = (json_str, userid)
    dbcursor.execute(sql, val)
    sqlconnect.commit()

def replace_item_in_inventory(inventory, item):
    for i in inventory["inventory"]:
        if item["id"] == i["id"]:
            #user has this item in their inventory
            inventory["inventory"].remove(i)
            inventory["inventory"].append(item)
            return
    
    return False

# returns an item if it is found in the inventory or false if it is not.
def search_inventory_for_item(inventory, item):
    for i in inventory["inventory"]:
        if item["id"] == i["id"]:
            #user has this item in their inventory
            return i
    
    return False

# drop a random item for specified userid
def surprise_mechanics(userid):
    roll = random.randint(0, len(itemValues))
    item = get_item_by_ID(roll)
    add_to_inventory(userid, item)
    return "You found: " + item["name"]
    
# def surprise_mechanics(userid):
#     roll = random.randint(0,10)
#     if roll == 0:
#         subroll = random.randint(1,10)
#         if(subroll == 1):
#             add_to_inventory(userid, get_item_by_ID(6))
#             return "You found **saronite armor**"
#         if(subroll == 2):
#             add_to_inventory(userid, get_item_by_ID(10))
#             return "You found a **saronite helmet**"
#         else:
#             add_to_inventory(userid, get_item_by_ID(3))
#             return "You found an **iron sword!**"
#     if roll <= 2:
#         roll = random.randint(1,2)
#         if roll < 2:
#             add_to_inventory(userid, get_item_by_ID(2))
#             return "You found a wooden sword"
#         else:
#             add_to_inventory(userid, get_item_by_ID(5))
#             return "You found steel armor"
#     if roll <= 5:
#         coincount = random.randint(10,30)
#         add_coins(userid, coincount)
#         return "You found " + str(coincount) + " coins."
#     if roll > 5:
#         subroll = random.randint(1,2)
#         if subroll == 1:
#             if roll <= 7:
#                 add_to_inventory(userid, get_item_by_ID(1))
#                 return "You found a *shitty* sword. :poop:"
#             else:
#                 add_to_inventory(userid, get_item_by_ID(4))
#                 return "You found leather armor"
#         else:
#             subroll = random.randint(7,9)
#             reward = get_item_by_ID(subroll)
#             add_to_inventory(userid, reward)
#             return "You found a " + reward["name"]
    

#   returns a string detailing the user's current status (AI helped)
def status(userid):
    try:
        dbcursor.execute("SELECT level, HP, coins, weapon, armor, head, experience_points FROM users WHERE id=" + str(userid))
        result = dbcursor.fetchone()
        if result is None:
            raise ValueError("Result is None")

        level = result[0]
        HP = result[1]
        coins = result[2]
        weapon = get_item_by_ID(result[3])
        armor = get_item_by_ID(result[4])
        head = get_item_by_ID(result[5])
        XP = result[6]
        print("Status: " + str(result))
        status_msg = "**Level**: " + str(level) + "\n**HP**: "+ str(HP) +"\n**Coins**: " + str(coins) + "\n**Weapon**: " + weapon["name"] + " (dps: " + str(weapon["dps"]) + ")\n**Armor**: " + armor["name"] + " (defense: " + str(armor["armor"]) + ")\n**Helm**: " + head["name"] + " (defense: " + str(head["armor"]) + ")\n**Experience Points**: " + str(result[5])
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
                slot = i["slot"]
                
                dbcursor.execute("SELECT "+slot+" FROM users WHERE id=" + str(userid))

                result = dbcursor.fetchone()
                equippeditem = get_item_by_ID(result[0])
                add_to_inventory(userid, equippeditem)
                sql = "UPDATE users SET "+slot+" = %s WHERE id= %s"
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
            if i["quantity"] == 1:
                userinv["inventory"].remove(i)
                print("removed stack")
            elif i["quantity"] > 1:
                i["quantity"] -= 1
                print("removed 1 from stack")
            json_str = json.dumps(userinv)
            sql = "UPDATE inventories SET items = %s WHERE id = %s"
            val = (json_str, userid)
            dbcursor.execute(sql, val)
            sqlconnect.commit()
            print(f"Removed item from inventory: {i}")
            return True

def unequip(userid, type):
    if type == "weapon":
        dbcursor.execute("SELECT weapon FROM users WHERE id=" + str(userid))
        result = dbcursor.fetchone()
        equippeditem = get_item_by_ID(result[0])
        add_to_inventory(userid, equippeditem)
        dbcursor.execute("UPDATE users SET weapon = 0 WHERE id=" + str(userid))
        sqlconnect.commit()
        return "Weapon unequipped, " + str(get_item_by_ID(result[0])["name"]) + " returned to inventory"
    
    if type == "armor" or type == "head":

        dbcursor.execute("SELECT "+type+" FROM users WHERE id=" + str(userid))
        result = dbcursor.fetchone()
        
        equippeditem = get_item_by_ID(result[0])
        print(equippeditem)
        add_to_inventory(userid, equippeditem)
        dbcursor.execute("UPDATE users SET "+type+" = 0 WHERE id=" + str(userid))
        sqlconnect.commit()
        return "Armor unequipped, " + str(get_item_by_ID(result[0])["name"]) + " returned to inventory"
    
    return "usage: !rpg unequip weapon, or !rpg unequip armor"

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

def get_user_armor(userid):
    dbcursor.execute("SELECT armor, head FROM users WHERE id = " + str(userid))
    result = dbcursor.fetchone()
    
    armor = get_item_by_ID(result[0])
    print(armor)
    head = get_item_by_ID(result[1])
    print(head)
    retval = [armor, head]
    return retval

def add_xp(userid, xp):
    dbcursor.execute("SELECT experience_points FROM users WHERE id = " + str(userid))
    result = dbcursor.fetchone()
    userxp = result[0] + xp
    sql = "UPDATE users SET experience_points = %s WHERE id = %s"
    vals = (userxp, userid)
    dbcursor.execute(sql, vals)
    sqlconnect.commit()
    print(str(xp) + " XP points rewarded to " + str(userid))

def check_player_alive(userid):
    dbcursor.execute("SELECT HP FROM users WHERE id = " + str(userid))
    result = dbcursor.fetchone()
    userHP = result[0]
    if userHP <= 0:
        return False
    return userHP

def take_damage(userid, damage):

    print("initial damage value: " + str(damage))
    armors = get_user_armor(userid)
    armor = armors[0]
    head = armors[1]
    defense = armor["armor"] + head["armor"]
    mitigation = round(0.1 * defense)
    onepercent = round(damage / 100)
    subtractvalue = onepercent * mitigation
    damage = damage - subtractvalue
    print("processed damage value: " + str(damage))

    dbcursor.execute("SELECT HP FROM users WHERE id = " + str(userid))
    result = dbcursor.fetchone()
    userHP = result[0]
    userHP = userHP - damage
    dbcursor.execute("UPDATE users SET HP = " + str(userHP) + " WHERE id = " + str(userid))
    sqlconnect.commit()
    returnvals = {}
    returnvals["string"] = "You took " +str(damage)+" damage, you now have "+str(userHP)+" HP."
    if userHP <= 0:
        returnvals["string"] += "\nYou are dead. You must wait to be revived."
    return returnvals

def use_item(userid, itemname):
    item = get_item_by_name(itemname)
    returnvals = {}
    if (item == False):
        returnvals["string"] = "Item not found."
        return returnvals
    
    inventory = get_inventory(userid)
    if search_inventory_for_item(inventory, item) == False:
        returnvals["string"] = "You don't have any of those."
        return returnvals
    
    if("HP" in item):
        remove_from_inventory(userid, item["id"])
        healuser(userid, item["HP"])
        returnvals["string"] = "Using the " + item["name"] + " healed you for " + str(item["HP"])
        return returnvals
    else:
        returnvals["string"] = "This object cannot be used."
        return returnvals
    
def healuser(userid, value):
    dbcursor.execute("SELECT HP FROM users WHERE id = " + str(userid))
    result = dbcursor.fetchone()
    userHP = result[0]
    userHP += value
    dbcursor.execute("UPDATE users SET HP = " + str(userHP) + " WHERE id = " + str(userid))
    sqlconnect.commit()