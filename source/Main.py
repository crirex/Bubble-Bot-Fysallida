# Work with Python 3.6
import random
import asyncio
from discord import Game
from discord.ext.commands import Bot

BOT_PREFIX = "+"
TOKEN = "NTM0NTUzNTM0OTE0NjI1NTY2.Dx7SMw.lnPefS-6vjOvlRqjFBiiHmpWoH0"

client = Bot(command_prefix=BOT_PREFIX)


class TrappedUser:
    def __init__(self, user_mention, bubble_type, bubble_color):
        self.user_mention = user_mention
        self.bubble_type = bubble_type
        self.bubble_color = bubble_color


trappedUsers = []


def read_trapped():
    f = open("../resource/TrappedUsers.bin", "r")
    all_data = f.read().splitlines()
    index = 0
    for data in all_data:
        if index == 0:
            user_mention = data
            index = 1
        elif index == 1:
            bubble_type = data
            index = 2
        elif index == 2:
            bubble_color = data
            trappedUsers.append(TrappedUser(user_mention, bubble_type, bubble_color))
            index = 0

    f.close()


def write_trapped():
    f = open("../resource/TrappedUsers.bin", "w")
    for current_user in trappedUsers:
        f.write(current_user.user_mention + '\n')
        f.write(current_user.bubble_type + '\n')
        f.write(current_user.bubble_color + '\n')
    f.close()


class TextFilter:
    def __init__(self, text, play_type='#', bubble_type='#'):
        self.text = text
        self.play_type = play_type
        self.bubble_type = bubble_type


class MultipleTextFilters:
    def __init__(self):
        self.text_possibilities = []
        # read from file

    def get_filtered_possibility(self, play_type='#', bubble_type='#'):

        all_play_types = [
            "trap",
            "squish",
            "sit"
        ]

        first_filtered_possibilities = []

        for possibility in self.text_possibilities:
            if possibility.bubble_type == bubble_type:
                first_filtered_possibilities.append(possibility)

        second_filtered_possibilities = []

        if play_type != '#':
            for possibility in first_filtered_possibilities:
                if possibility.play_type == play_type:
                    second_filtered_possibilities.append(possibility)
        else:
            second_filtered_possibilities = first_filtered_possibilities

        if not second_filtered_possibilities:
            second_filtered_possibilities = self.text_possibilities

        if second_filtered_possibilities:
            message = (random.choice(second_filtered_possibilities)).text
        else:
            message = "It seems like i couldn't find anything to do."

        return message


def trapped(ctx, user):
    if type(user) is str:
        for current_user in trappedUsers:
            if user == current_user.user_mention:
                return True
    return False


def get_all_members(ctx):
    all_users = []
    for current_user in ctx.message.server.members:
        if (current_user.status != "offline") & (
                current_user.status != "busy") & (
                not current_user.bot) & (
                not trapped(ctx, current_user.mention)):
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


@client.command(name='introduction',
                description="I introduce myself.",
                brief="I give you a big text with my character details.",
                pass_context=True)
async def introduction(ctx):
    print(str(ctx.message.server.members))
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


@client.command(name='bubble',
                description="Bubbles someone",
                brief="I use bubbles to play with someone",
                aliases=['putInABubble', 'putInBubble'],
                pass_context=True)
async def bubble(ctx, user=None, bubble_type='#', color_type='#', play_type='#'):
    if user is None:
        all_users = get_all_members(ctx)
        if not all_users:
            await client.say("No eligible member has been found.")
            return
        user = (random.choice(all_users)).mention
    else:
        if trapped(ctx, user):
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

    all_text_type = MultipleTextFilters()

    all_text_type.text_possibilities.append(TextFilter("I create a {1} rubber bubble throwing it towards "
                                                       "{0} as it surrounds {0} in it’s rubbery walls "
                                                       "squeezing them tight then {0} plopped inside trapped "
                                                       "in my bubble", "trap", "rubber"))

    all_text_type.text_possibilities.append(TextFilter("I blow a {1} soap bubble and put {0} in it, as {0} "
                                                       "floats a few inches in the air.", "trap", "soap"))

    all_text_type.text_possibilities.append(TextFilter("I began to form a {1} rubber sphere bouncing it towards {0} "
                                                       "then jumping on top of the rubber bubble and squeezed {0} "
                                                       "underneath leaving {0} helpless until {0} sank inside "
                                                       "and got trapped", "trap", "rubber"))

    all_text_type.text_possibilities.append(TextFilter("The ground shakes a bit underneath {0} as two {1} half "
                                                       "spheres pop out from both sides of {0} and clamp "
                                                       "together locking {0} inside a {1} glass Ball", "trap", "glass"))

    all_text_type.text_possibilities.append(TextFilter("There is a lot of multicolor lights and a rainbow bubble is "
                                                       "formed, wobbling towards {0}, absorbing {0} inside the bubble "
                                                       ", with no way of using any "
                                                       "sort of magic to escape.", "trap", "magic"))

    all_text_type.text_possibilities.append(TextFilter("I make a small {1} plastic bubble. It inflates right in front "
                                                       "of {0} as {0} can't move out of the way. {0}'s eyes are "
                                                       "closed while {0} can feel the pressure of the bubble "
                                                       "intensifying, then {0} feels like passing through something. "
                                                       "{0} opens his eyes only to see that {0} is now inside the"
                                                       " bubble that now has the same size "
                                                       "as {0} is.", "trap", "plastic"))

    all_text_type.text_possibilities.append(TextFilter("I blow a {1} plastic bubble directly out of {0}'s screen and "
                                                       "it gets big so fast that {0} couldn't react and gets "
                                                       "trapped inside the bubble.", "trap", "plastic"))

    all_text_type.text_possibilities.append(TextFilter("I pulled out a bazooka and aimed it at {0} pressing the "
                                                       "trigger then a loud BOOOING sound came from the end of "
                                                       "it launching a {1} rubber bubble at {0} then went above HIS "
                                                       "head and come down smooshing {0} inside.", "trap", "rubber"))

    color_type = color_type.lower()
    play_type = play_type.lower()
    bubble_type = bubble_type.lower()

    response: str = all_text_type.get_filtered_possibility(play_type, bubble_type)

    trappedUsers.append(TrappedUser(user, bubble_type, color_type))
    write_trapped()
    await client.say(response.format(user, color_type))


@client.command(name='pop',
                description="Let's someone free.",
                brief="I get someone out of their bubble zone.",
                aliases=['letGo', 'popBubble', 'leave', 'lego', 'letgo', 'popbubble', 'release'],
                pass_context=True)
async def leave_bubble(ctx, user=None):
    if type(user) is str:
        for current_user in trappedUsers:
            if user == current_user.user_mention:
                removed_user = current_user
                trappedUsers.remove(current_user)
                write_trapped()
                await client.say("The {2} {1} bubble in which {0} was just pops "
                                 "and {0} is now free.".format(removed_user.user_mention, removed_user.bubble_type,
                                                               removed_user.bubble_color))
                return

        await client.say("{0} isn't trapped in any kind of bubble. "
                         "Maybe {0} needs to be in one :3".format(user))
    else:
        await client.say("{0}, you need to specify who to let go.".format(ctx.message.author.mention))


@client.command(name='test',
                description="test",
                brief="Won't exist in final version",
                aliases=['t'])
async def test():
    await client.say("```\n"
                     + "uhh" +
                     "\n```")


# Just initialize stuff
@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with bubbles."))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


# List all the servers from time to time so we could know where the bot is located
async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(3600)


# We take all the messages and process them to see if we can interact with someone
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return


read_trapped()
client.loop.create_task(list_servers())
client.run(TOKEN)
