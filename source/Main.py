# Work with Python 3.6
import random
import asyncio

import aiohttp
import json
from discord import Game
from discord.ext.commands import Bot

BOT_PREFIX = "+"
TOKEN = "NTM0NTUzNTM0OTE0NjI1NTY2.Dx7SMw.lnPefS-6vjOvlRqjFBiiHmpWoH0"

client = Bot(command_prefix=BOT_PREFIX)


@client.command(name='introduction',
                description="I introduce myself.",
                brief="I give you a big text with my character details.")
async def introduction():
    introduction_message = "Hi ^^, my name is Fysallida and I am a shy and small bubble bot. " \
                           "I go from a device to another and create bubbles of all sizes. " \
                           "I generate them by hacking into 3D-Printers or by using some of my magic " \
                           "to blow bubbles directly out of the monitor or TV " \
                           "(phone screens too, but they are way harder to blow through :confounded: ). " \
                           "The bubbles I generate are super resistant and can be made out of soap, rubber, plastic " \
                           "or gum (glass too, but those make a dangerous mess when they break :pensive: ) " \
                           "and I can control them at my will to play with somebody :3 " \
                           ". If you want to know how to use me just type \"+help\" and I'll be sure to help."
    await client.say(introduction_message)


@client.command(name='myHelp',
                description="I give you my commands.",
                brief="I give a legend and tell you how to use me.")
async def help_output():
    help_message = "--- Legend ---\n" \
                           "-> -> definition\n " \
                           "+ -> it\'s the command you write so that i can know you want to use ME, " \
                           "I mean access my functions.\n" \
                           "[] -> is a field you are required to fill. " \
                           "( You don't need to put the [] when writing the function ).\n" \
                           "{} -> is a field you are not required to fill. " \
                           "( You don't need to put the {} when writing the function ).\n" \
                           "() -> comments\n" \
                           "--- The following commands exist for your use ---\n" \
                           "+help -> Shows you all my commands...again.\n" \
                           "+introduction -> I will introduce myself :blush:\n" \
                           "+bubble {@Name | Name} {Soap | Rubber | Gum | Plastic | Glass} " \
                           "{Trap | Squish | Sit} -> This command will be used so that i could use " \
                           "my powers to create bubbles and use them to play with someone. " \
                           "If you dont pick anything in a field then I will just do random things.\n" \
                           "+art -> Will randomly show a bubble art from my archive " \
                           "( This should be updated daily, but it\'s not implemented at the moment. )\n" \
                           "+story -> Will randomly write a bubble story from my archive " \
                           "( Again, like the above, but this could be harder or easier to implement. )\n" \
                           "+music [url / name] -> Well like any other bot I should be able to play some music " \
                           "as well. ( I guess it will only be from youtube, but who knows. )\n" \
                           "Thanks for using me and have a bubbly day :smile: .\n"

    await client.say(help_message)


@client.command(name='hello',
                description="Greets you back.",
                brief="Greets you back with some random phrase.",
                aliases=['hi', 'greetings', 'yo', 'hey'],
                pass_context=True)
async def hello(context):
    possible_responses = [
        'Hi',
        'Hello',
        'Hey',
        'Greetings',
    ]
    await client.say(random.choice(possible_responses) + " " + context.message.author.mention)


@client.command(name='bubble',
                description="Bubbles someone",
                brief="I use bubbles to play with someone",
                pass_context=True)
async def bubble(context, user):
    possible_responses = [
        'I blow a bubble and put ' + user + " in it, as he floats a few inches in the air.",
    ]
    await client.say(random.choice(possible_responses))


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with bubbles."))
    print("Logged in as " + client.user.name)


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(3600)


client.loop.create_task(list_servers())
client.run(TOKEN)
