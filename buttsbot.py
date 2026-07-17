# # this bot randomly responds to someone's message and sends it back,
# # but replaces one word in the message with the word "butt"
# import os
# import discord
# import random

# from dotenv import load_dotenv

# load_dotenv()
# TOKEN = os.getenv('BUTTSBOT_TOKEN')

# client = discord.Client(intents=discord.Intents.all())

# @client.event
# async def on_message(message):
#     if random.randint(0,60) != 1:
#         return

#     word_list = message.content.split()

#     random_index = random.randint(0, len(word_list) - 1)
#     word_list[random_index] = "butt"

#     new_string = " ".join(word_list)

#     await message.channel.send(new_string)

# client.run(TOKEN)

import os
import random
import discord
import nltk

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BUTTSBOT_TOKEN")

# Download the tagger once (only needed the first time)
nltk.download("averaged_perceptron_tagger_eng")

client = discord.Client(intents=discord.Intents.all())

NOUN_TAGS = {"NN", "NNS", "NNP", "NNPS"}

@client.event
async def on_message(message):
    if message.author == client.user and random.randint(0, 60) != 1:
        return
    
    if "@1111148610042732584" not in message.content:
        if random.randint(0, 60) != 1:
            return

    word_list = message.content.split() # split the discord message into a usable array

    # Get the part-of-speech tag for every word
    tagged_words = nltk.pos_tag(word_list)

    # Find the indices of all nouns
    noun_indices = []

    for i, (_, tag) in enumerate(tagged_words):
        if tag in NOUN_TAGS:
            noun_indices.append(i)

    # If there aren't any nouns, do nothing
    if not noun_indices:
        return

    # Pick a random noun to replace
    random_index = random.choice(noun_indices)
    word_list[random_index] = "butt"

    new_string = " ".join(word_list)

    await message.channel.send(new_string)

client.run(TOKEN)