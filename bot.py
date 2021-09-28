# Author: Jack Carter
# Bot for private Discord Server
import unicodedata
import os
import discord
from dotenv import load_dotenv
import random
from configparser import ConfigParser
import asyncio
from datetime import datetime
from discord.ext.commands import Bot
from keep_alive import keep_alive

keep_alive()
##########################################
#               CONSTANTS
##########################################
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
ROLE_MSG_ID = os.getenv('ROLE_MSG_ID')
SPAM_CHANNEL_ID = os.getenv('SPAM_CHANNEL_ID')
LEAVE_CHANNEL_ID = os.getenv('LEAVE_CHANNEL_ID')

##########################################
#               GLOBAL VARIABLES
##########################################
client = discord.Client()
config = ConfigParser()
config.optionxform = str
config.read("config.ini")
spam_detection = {}
monty_quotes = [
    "A newt?!", "Your father smells of elderberries",
    "If we built this large wooden badger", "One, Two, Five - 3 sir! - Three!",
    "And Saint Attila raised the hand grenade up on high, saying, "
    "'O Lord, bless this Thy hand grenade that, with it, "
    "Thou mayest blow Thine enemies to tiny bits in Thy mercy.' "
    "And the Lord did grin, and the people did feast upon the lambs"
    " and sloths and carp and anchovies and orangutans and "
    "breakfast cereals and fruit bats and large chu--", "They're doctors?!",
    "Please! Please! This is supposed to be a happy occasion! ",
    "Let's not bicker and argue about who killed who."
]

##########################################
#               CONFIG
##########################################
enable_spam_detection = config.get("settings", "enable_spam_detection")
spam_interval = int(config.get("settings", "spam_interval"))
spam_min_messages = int(config.get("settings", "spam_min_messages"))


##########################################
#               ON START
##########################################
@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")
    print(f"Guild: {GUILD}")

    guild = discord.utils.get(client.guilds, name=GUILD)
    print(f'{client.user} is connected to the following guild:\n'
          f'{guild.name}(id: {guild.id})')

    # Clears the spam log at configured interval
    if enable_spam_detection == "true":
        while True:
            await asyncio.sleep(spam_interval)
            spam_detection.clear()


##########################################
#               ON MEMBER LEAVE
##########################################
@client.event
async def on_member_leave(member):
    await client.get_channel(
        int(LEAVE_CHANNEL_ID)
    ).send(f"{member.name} has departed")


##########################################
#               ON MESSAGE
##########################################
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    ##########################################
    #               SPAM DETECTION
    ##########################################
    if enable_spam_detection == "true" and message.channel.id != int(
            SPAM_CHANNEL_ID):
        if message.author in spam_detection:
            current_msg = spam_detection.get(message.author)
            spam_detection.update({message.author: current_msg + 1})
            current_msg = spam_detection.get(message.author)
            if current_msg >= spam_min_messages:
                await message.channel.send('{0.name} be quiet'.format(
                    message.author))
                spam_detection.update({message.author: 0})
        else:
            spam_detection.update({message.author: 0})

    ##########################################
    #               FUN COMMANDS
    ##########################################
    if message.content.lower() == "montypython":
        response = random.choice(monty_quotes)
        await message.channel.send(response)

    if message.content.lower() == "!gibquote":
        f = open("quotes.txt")
        quotes = f.readlines()
        quote = random.choice(quotes)
        await message.channel.send(quote)
        

    ##########################################
    #               ADMIN COMMANDS
    ##########################################
    if message.content == "!restart" and message.author.guild_permissions.administrator:
        print("Restarting...")
        response = "Restarting..."
        await message.channel.send(response)
        os.system('python startup.py')
        exit()

##########################################
#              ADD ROLES
##########################################
@client.event
async def on_raw_reaction_add(payload):
    # Setting up required variables
    guild_id = payload.guild_id
    guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
    member = await (await client.fetch_guild(payload.guild_id
                                             )).fetch_member(payload.user_id)
    message_id = payload.message_id
    # If the message reacted to was the message specified in the config
    if message_id == int(ROLE_MSG_ID):
        # Iterating over the keys in the roles category
        for (key, val) in config.items("roles"):
            # Had to do this stuff just to be able to check for equality. The emoji is encoded and then decoded
            # and changed to uppercase in order to be able to be viewed the same as the key
            emoji = payload.emoji.name.encode('unicode-escape').decode(
                'ASCII').upper()
            if emoji == key:
                role = discord.utils.get(guild.roles, name=val)
                await member.add_roles(role)
                break


##########################################
#              REMOVE ROLES
##########################################
@client.event
async def on_raw_reaction_remove(payload):
    # Setting up required variables
    guild_id = payload.guild_id
    guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
    member = await (await client.fetch_guild(payload.guild_id
                                             )).fetch_member(payload.user_id)
    message_id = payload.message_id
    # If the message reacted to was the message specified in the config
    if message_id == int(ROLE_MSG_ID):
        # Iterating over the keys in the roles category
        for (key, val) in config.items("roles"):
            # Had to do this stuff just to be able to check for equality. The emoji is encoded and then decoded
            # and changed to uppercase in order to be able to be viewed the same as the key
            emoji = payload.emoji.name.encode('unicode-escape').decode(
                'ASCII').upper()
            if emoji == key:
                role = discord.utils.get(guild.roles, name=val)
                await member.remove_roles(role)
                break


##########################################
#               EXCEPTIONS
##########################################
@client.event
async def on_error(event, *args, **kwargs):
    with open("err.log", "a") as f:
        if event == "on_message":
            f.write(f"Unhandled Message: {args[0]}\n")
        else:
            raise


client.run(TOKEN)
