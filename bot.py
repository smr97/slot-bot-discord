import os
import re
import datetime

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


salutations = ["hi", "hello", "namaste", "hey", "bot", "yo", "help", "usage"]

usage = """
I have been created to log visa interview slots.
If you were lucky enough to get a slot, just type in the following message PER SLOT that you found:
    got an interview slot at {location} on DD/MM/YY.
If you haven't found any slot yet, just type in one message PER SEARCH that you made, in the following manner:
    Tried date DD/MM/YY at {location}
"""

locations = ["mumbai", "delhi", "kolkata", "hyderabad", "chennai"]


def parse_message(found_string, status):
    loc = next(_l for _l in locations if _l in found_string)
    match = re.search(r"(\d+/\d+/\d+)", found_string).group(1)
    date = datetime.datetime.strptime(match, "%d/%m/%y")
    print(f"status {status} {loc} on {date}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(f"Got message {message.content} from {message.author}")
    message.content = message.content.lower()
    status = True if "got" in message.content else False
    try:
        parse_message(message.content, status)
    except StopIteration:
        await message.channel.send(
            "Couldn't figure out the location, please try again, ask for help maybe?"
        )
        return
    except ValueError:
        await message.channel.send(
            "Couldn't figure out the date, please try again, ask for help maybe?"
        )
        return
    except AttributeError:
        await message.channel.send(
            "Couldn't figure out the date, please try again, ask for help maybe?"
        )
        return
    except Exception as e:
        print(e)
        await message.channel.send(
            "Didn't get you, please ask for help and try again. Else, report a bug to smr97"
        )
        return
    if status:
        await message.channel.send(
            "I see that you got a slot, that is great! I have noted down the details. If this is not the case, report a bug to smr97"
        )
    else:
        await message.channel.send("I see that you didn't get a slot, hang in there!")
    if any(salutation in message.content for salutation in salutations):
        await message.channel.send(f"Hi {message.author}, {usage}")


client.run(TOKEN)
