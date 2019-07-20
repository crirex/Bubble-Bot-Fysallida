#!/usr/bin/python3.6
# Work with Python 3.6
from discord import Game, Message
from discord.ext import commands
from discord.ext.commands import Bot

from globals import *
from component import *
from jsons import Writeback

client: Bot = Bot(command_prefix=config.prefix, owner_id=config.owner)


# Closes the bot. Can only be used by me.
# noinspection PyUnusedLocal
@client.command(name='logout',
                pass_context=True)
@commands.is_owner()
async def logout(ctx):
    print("Logging out")
    await client.logout()
    # nothing past here is executed


# Verify each message to see if it has something to do with the bot, then responds to them
@client.event
async def on_message(message: Message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    if message.content.startswith(client.command_prefix):
        await client.process_commands(message)
        return

    give_message_to_bot: bool = False
    message_to_give: str = message.content
    if message.content.startswith("Bubble Bot Fysallida "):
        message_to_give = message_to_give.replace("Bubble Bot Fysallida ", '', 1)
        give_message_to_bot = True
    elif message.content.startswith("Fysallida "):
        message_to_give = message_to_give.replace("Fysallida ", '', 1)
        give_message_to_bot = True
    elif message.content.startswith("Bubble Bot "):
        message_to_give = message_to_give.replace("Bubble Bot ", '', 1)
        give_message_to_bot = True
    elif message.content.startswith(client.user.mention):
        message_to_give = message_to_give.replace(client.user.mention + " ", '', 1)
        give_message_to_bot = True

    if give_message_to_bot:
        message.content = client.command_prefix + message_to_give
        await client.process_commands(message)


# Just initialize stuff
@client.event
async def on_ready():
    await client.change_presence(activity=Game(name="with bubbles."))

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


if __name__ == "__main__":
    client.add_cog(Writeback(client))
    client.add_cog(Preferences(client))
    client.add_cog(Help(client))
    client.add_cog(Bubbles(client))
    client.add_cog(Voice(client))
    client.add_cog(Background(client))
    client.add_cog(Time(client))
    client.add_cog(Videos(client))
    client.add_cog(Pictures(client))
    client.run(config.token)
