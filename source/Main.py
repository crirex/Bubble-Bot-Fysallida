#!/usr/bin/python3.6
# Work with Python 3.6
import asyncio

from discord import Game, Message, TextChannel
from discord.ext.commands import Bot

from component import *
from jsons import trapped_users_json

client: Bot = Bot(command_prefix=config.prefix)


# Closes the bot. Can only be used by me.
@client.command(name='logout',
                pass_context=True)
async def logout(ctx):
    if ctx.message.author.id == config.owner:
        print("Logging out")
        await client.logout()
        # nothing past here is executed


# Test
@client.command(name='test',
                description="test",
                brief="Won't exist in final version",
                aliases=['t'])
async def test(ctx):
    await ctx.message.channel.send(round(time.time() - start_time))
    print(time.time())
    print(time.time() - start_time)
    if time.time() - start_time > 15:
        await ctx.message.channel.send("some time has passed")


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


# List all the servers from time to time so we could know where the bot is located
async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.guilds:
            print(server.name)
        await asyncio.sleep(3600)


async def verify_pop():
    await client.wait_until_ready()
    while not client.is_closed:
        for trapped_user in trapped_users:
            if time.time() - trapped_user.time > maximum_bubble_time:
                channel = client.get_channel(trapped_user.channel)
                user = channel.guild.get_member(trapped_user.user) if isinstance(channel, TextChannel)\
                    else client.get_user(trapped_user.user)
                await client.get_channel(trapped_user.channel).send(
                    "After some time the {2} {1} bubble fails to hold its "
                    "composure and pops freeing {0}. "
                    .format(user.mention if get_user_prefs(user.id).ping else user.display_name,
                            trapped_user.bubble_type,
                            trapped_user.bubble_color))
                trapped_users.remove(trapped_user)
                dump_json(trapped_users, trapped_users_json)
        await asyncio.sleep(5)


if __name__ == "__main__":
    client.add_cog(Help(client))
    client.add_cog(Bubbles(client))
    client.add_cog(Preferences(client))
    client.add_cog(Voice(client))
    client.loop.create_task(list_servers())
    client.loop.create_task(verify_pop())
    client.run(config.token)
