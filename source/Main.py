#!/usr/bin/python3.6
# Work with Python 3.6
import json
import random
import asyncio
import time
from discord import Game, Message
from discord.ext.commands import Bot

client: Bot = Bot(command_prefix="+")

start_time = time.time()

trapped_users = json.load(open("TrappedUsers.json", "r"))
trapping_text = json.load(open("TrappingText.json", "r"))

maximum_bubble_time = 43200  # seconds = 12 hours
maximum_number_of_popping_times = 3


class TextFilter:
    def __init__(self, text, play_type='#', bubble_type='#'):
        self.text = text
        self.play_type = play_type
        self.bubble_type = bubble_type


def get_filtered_possibility(play_type='#', bubble_type='#'):
    first_filtered_possibilities = []

    for possibility in trapping_text:
        if possibility["bubble_type"] == bubble_type:
            first_filtered_possibilities.append(possibility)

    second_filtered_possibilities = []

    if play_type != '#':
        for possibility in first_filtered_possibilities:
            if possibility["play_type"] == play_type:
                second_filtered_possibilities.append(possibility)
    else:
        second_filtered_possibilities = first_filtered_possibilities

    if not second_filtered_possibilities:
        second_filtered_possibilities = trapping_text

    if second_filtered_possibilities:
        message = (random.choice(second_filtered_possibilities))["text"]
    else:
        message = "It seems like i couldn't find anything to do."

    return message


def trapped(user):
    if type(user) is str:
        for current_user in trapped_users:
            if user == current_user["user_mention"]:
                return True
    return False


def get_all_members(ctx):
    all_users = []
    for current_user in ctx.message.server.members:
        if (current_user.status != "offline") & (
                current_user.status != "busy") & (
                not current_user.bot) & (
                not trapped(current_user.mention)):
            all_users.append(current_user)
    return all_users


def get_random_bubble_type():
    all_bubble_types = [
        "soap",
        "rubber",
        "gum",
        "plastic",
        "glass",
        "magic"
    ]
    return random.choice(all_bubble_types)


def get_random_color():
    all_colors = [
        "orange",
        "blue",
        "green",
        "red",
        "yellow",
        "white",
        "pink",
        "purple",
        "teal",
        "black",
    ]
    return random.choice(all_colors)


# The command for introduction
@client.command(name='introduction',
                description="I introduce myself.",
                brief="I give you a big text with my character details.",
                pass_context=True)
async def introduction(ctx):
    introduction_message = "Hi ^^, my name is Fysallida and I am a shy and small bubble bot. " \
                           "I go from a device to another and create bubbles of all sizes. " \
                           "I generate them by hacking into 3D-Printers or by using some of my magic " \
                           "to blow bubbles directly out of the monitor or TV " \
                           "(phone screens too, but they are way harder to blow through :confounded: ). " \
                           "The bubbles I generate are super resistant and can be made out of soap, rubber, plastic " \
                           "or gum (glass too, but those make a dangerous mess when they break :pensive: ) " \
                           "and I can control them at my will to play with somebody :3 " \
                           ". If you want to know how to use me just type \"+help\" and I'll be sure to help."
    await client.send_message(ctx.message.author, introduction_message)


# My help beside the normal help
@client.command(name='myHelp',
                description="I give you my commands.",
                brief="I give a legend and tell you how to use me.",
                pass_context=True)
async def help_output(ctx):
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
                   "If you don't pick anything in a field then I will just do random things.\n" \
                   "+art -> Will randomly show a bubble art from my archive " \
                   "( This should be updated daily, but it\'s not implemented at the moment. )\n" \
                   "+story -> Will randomly write a bubble story from my archive " \
                   "( Again, like the above, but this could be harder or easier to implement. )\n" \
                   "+music [url / name] -> Well like any other bot I should be able to play some music " \
                   "as well. ( I guess it will only be from youtube, but who knows. )\n" \
                   "Thanks for using me and have a bubbly day :smile: .\n"

    await client.send_message(ctx.message.author, help_message)


# Hello command
@client.command(name='hello',
                description="Greets you back.",
                brief="Greets you back with some random phrase.",
                aliases=['hi', 'greetings', 'yo', 'hey'],
                pass_context=True)
async def hello(ctx):
    possible_responses = {
        'Hi',
        'Hello',
        'Hey',
        'Greetings'
    }
    await client.say(random.choice(possible_responses) + " " + ctx.message.author.mention)


# Puts someone in a bubble
@client.command(name='bubble',
                description="Bubbles someone",
                brief="I use bubbles to play with someone",
                aliases=['putInABubble', 'putInBubble'],
                pass_context=True)
async def bubble(ctx, user=None, bubble_type='#', color_type='#',
                 seconds_trapped: int = maximum_bubble_time, play_type='#', ):
    if user is None:
        all_users = get_all_members(ctx)
        if not all_users:
            await client.say("No eligible member has been found.")
            return
        user = (random.choice(all_users)).mention
    else:
        if trapped(user):
            await client.say("{0} is already trapped in a bubble and cannot be put in another one right now. "
                             "You could get him out of the bubble if you want to.".format(user))
            return
        if (user.lower() == "pop") | (user.lower() == "release"):
            user = bubble_type
            print(user)
            await client.say("{0}, you need to use the \"+pop @name\" command".format(ctx.message.author.mention))
            return

    if color_type == '#':
        color_type = get_random_color()

    if bubble_type == '#':
        bubble_type = get_random_bubble_type()

    color_type = color_type.lower()
    play_type = play_type.lower()
    bubble_type = bubble_type.lower()

    seconds_trapped = maximum_bubble_time - seconds_trapped
    response: str = get_filtered_possibility(play_type, bubble_type)
    user_channel = ctx.message.channel
    trapped_users.append({
        "user_mention": user,
        "bubble_type": bubble_type,
        "bubble_color": color_type,
        "time": time.time() - seconds_trapped,
        "channel": user_channel.id,
        "tries": 0
    })
    json.dump(trapped_users, open("TrappedUsers.json", "w"))
    await client.say(response.format(user, color_type))


# Free yourself or someone else someone from a bubble
@client.command(name='pop',
                description="Let's someone free.",
                brief="I get someone out of their bubble zone.",
                aliases=['letGo', 'popBubble', 'lego', 'letgo', 'popbubble', 'release'],
                pass_context=True)
async def leave_bubble(ctx, user=None):
    if user is None:
        user = ctx.message.author.mention

    if type(user) is str:
        for current_user in trapped_users:
            if ctx.message.author.mention == current_user:
                await client.say("{0} is inside a bubble and is unable to pop anyone else's bubble because of that, "
                                 "{0}'s actions being limited to the insides of the bubble"
                                 .format(user))
                return

        for current_user in trapped_users:
            if user == current_user["user_mention"]:
                if ctx.message.author.mention == user:
                    if current_user["tries"] >= maximum_number_of_popping_times:
                        text_to_say = ["The {2} {1} bubble in which {0} was just pops after so many tries to escape "
                                       "and {0} is now free. (Maybe there was some unknown force that let you free)",
                                       "I reach out and touch {0}'s {2} {1} bubble in which "
                                       "{0} was trapped in, after which it pops and {0} is now free."]

                        await client.say(random.choice(text_to_say).format(current_user["user_mention"],
                                                                           current_user["bubble_type"],
                                                                           current_user["bubble_color"]))
                        trapped_users.remove(current_user)
                        json.dump(trapped_users, open("TrappedUsers.json", "w"))
                        return

                    text_to_say = "{0} tries to pop the bubble but only manages to stretch it, " \
                                  "seeing how resilient it is and unable to pop it. " \
                                  "Only someone else may pop it or it will pop by itself after some time. "
                    if current_user["tries"] >= maximum_number_of_popping_times - 1:
                        text_to_say += "The bubble seems to have lost some of it's resistance after " \
                                       "so many attempts to free yourself."

                    await client.say(text_to_say.format(user))
                    current_user["tries"] += 1
                    json.dump(trapped_users, open("TrappedUsers.json", "w"))
                    return
                else:
                    await client.say("{3} pops the {2} {1} bubble in which {0} was just, freeing {0} "
                                     "from the bubbly, comfy prison".format(current_user["user_mention"],
                                                                            current_user["bubble_type"],
                                                                            current_user["bubble_color"],
                                                                            ctx.message.author.mention))
                    trapped_users.remove(current_user)
                    json.dump(trapped_users, open("TrappedUsers.json", "w"))
                    return

        await client.say("{0} isn't trapped in any kind of bubble. "
                         "Maybe {0} needs to be in one :3".format(user))
    else:
        await client.say("{0}, you need to specify who to let go.".format(ctx.message.author.mention))


# Just initialize stuff
@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with bubbles."))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


# Closes the bot. Can only be used by me.
@client.command(name='logout',
                pass_context=True)
async def logout(ctx):
    if ctx.message.author.mention == "<@142593360992010240>":
        if client.is_logged_in:
            await client.logout()
            print("Logged out")
            exit()


# Joins the voice channel of the person that used the command
@client.command(name='join',
                pass_context=True)
async def join_voice(ctx):
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)
    print("Joined voice channel")


# Leaves the voice channel
@client.command(name='leave',
                pass_context=True)
async def leave_voice(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()
    print("Left voice channel")


# List all the servers from time to time so we could know where the bot is located
async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(3600)


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
    if message.content.startswith("Bubble Bot Fysallida"):
        message_to_give = message_to_give.replace("Bubble Bot Fysallida ", '', 1)
        give_message_to_bot = True
    elif message.content.startswith("Fysallida"):
        message_to_give = message_to_give.replace("Fysallida ", '', 1)
        give_message_to_bot = True
    elif message.content.startswith("Bubble Bot"):
        message_to_give = message_to_give.replace("Bubble Bot ", '', 1)
        give_message_to_bot = True
    elif message.content.startswith(client.user.mention):
        message_to_give = message_to_give.replace(client.user.mention + " ", '', 1)
        give_message_to_bot = True

    if give_message_to_bot:
        message.content = "+" + message_to_give
        await client.process_commands(message)


# Test
@client.command(name='test',
                description="test",
                brief="Won't exist in final version",
                aliases=['t'])
async def test():
    await client.say(round(time.time() - start_time))
    print(time.time())
    print(time.time() - start_time)
    if time.time() - start_time > 15:
        await client.say("some time has passed")


async def verify_pop():
    await client.wait_until_ready()
    while not client.is_closed:
        for trapped_user in trapped_users:
            if time.time() - trapped_user["time"] > maximum_bubble_time:
                await client.send_message(client.get_channel(trapped_user["channel"]),
                                          "After some time the {2} {1} bubble fails to hold it "
                                          "composure and pops freeing {0}. ".format(trapped_user["user_mention"],
                                                                                    trapped_user["bubble_type"],
                                                                                    trapped_user["bubble_color"]))
                trapped_users.remove(trapped_user)
                json.dump(trapped_users, open("TrappedUsers.json", "w"))
        await asyncio.sleep(5)


if __name__ == "__main__":
    maximum_number_of_popping_times -= 1  # this is needed to adjust the constant to be the number of tries specified
    my_token = json.load(open("config.json", "r"))
    client.loop.create_task(list_servers())
    client.loop.create_task(verify_pop())
    client.run(my_token["token"])
