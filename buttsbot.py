# this bot randomly responds to someone's message and sends it back,
# but replaces one word in the message with the word "butt"
import os
import discord
import random

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BUTTSBOT_TOKEN')

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_message(message):
    if random.randint(0,60) != 1:
        return
    
    word_list = message.content.split()
    random_index = random.randint(0, len(word_list) - 1)
    word_list[random_index] = "butt"

    new_string = " ".join(word_list)

    await message.channel.send(new_string)

client.run(TOKEN)