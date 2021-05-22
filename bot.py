import os
import asyncio
import re
import datetime
from record import DateError, LocationError, MessageStore, StatError

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client()


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")
    for g in client.guilds:
        print(f"Connected to guild {g}")
    client.msg_store = MessageStore(maxsize=100)


salutations = ["hi", "hello ", "namaste ", "hey ", "bot ", "yo", "help", "usage"]

usage = """
I have been created to log visa interview slots.
If you were lucky enough to get a slot, just type in the following message PER SLOT that you found:
    got {location} on DD/MM/YY.
If you haven't found any slot yet, just type in one message PER SEARCH that you made, in the following manner:
    tried {location} on DD/MM/YY
"""


@client.event
async def on_message(message):
    if message.author == client.user or (
        message.guild is not None and client.user not in message.mentions
    ):
        return
    print(f"Got message {message.content} from {message.author}")
    message.content = message.content.lower()
    if any(message.content.startswith(s) for s in salutations):
        await message.channel.send(f"Hi {message.author}, {usage}")
        return
    status = client.msg_store.enqueue_message(
        message.content, str(message.author).split("#")[0]
    )
    if status:
        await message.channel.send(
            "I see that you got a slot, that is great! I have noted down the details. If this is not the case, report a bug to smr97"
        )
    else:
        await message.channel.send("I see that you didn't get a slot, hang in there!")


@client.event
async def on_disconnect():
    client.msg_store.flush_queues()


@client.event
async def on_error(some_event, *its_args, **kwargs):
    import sys

    extype, value, traceback = sys.exc_info()
    orig_message = None
    for _s in its_args + tuple(kwargs.values()):
        if isinstance(_s, discord.Message):
            orig_message = _s
            break

    print(f"Caught {extype} {value.base_exception if hasattr(value, 'base_exception') else None}: {traceback}")
    if isinstance(value, LocationError):
        await orig_message.channel.send(
            "Couldn't figure out the location, please try again, ask for help maybe?"
        )
    elif isinstance(value, DateError):
        await orig_message.channel.send(
            "Couldn't figure out the date, please try again, ask for help maybe?"
        )
    elif isinstance(value, StatError):
        await orig_message.channel.send(
            "Didn't understand whether you found a slot or not. If you did, type 'got <location> on DD/MM/YY"
        )
    else:
        await orig_message.channel.send(
            "Didn't get you, please ask for help and try again. Else, report a bug to smr97"
        )


client.run(TOKEN)
client.msg_store.flush_queues()
