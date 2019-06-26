import random
import json
import time
import typing
from json import JSONDecodeError

start_time = time.time()
maximum_bubble_time = 43200  # seconds = 12 hours
maximum_number_of_popping_times = 3

with open("config.json", "r") as config_json:
    config = json.load(config_json)
with open("TrappingText.json", "r") as trapping_text_json:
    trapping_text = json.load(trapping_text_json)
try:
    with open("TrappedUsers.json", "r") as trapped_users_json:
        trapped_users = json.load(trapped_users_json)
except (JSONDecodeError, IOError):
    trapped_users = []
trapped_users_json = open("TrappedUsers.json", "w+")
try:
    with open("UserPreferences.json", "r") as user_preferences_json:
        user_preferences = json.load(user_preferences_json)
except (JSONDecodeError, IOError):
    user_preferences = {}
user_preferences_json = open("UserPreferences.json", "r+")


def get_user_prefs(user_id: int):
    user_id = str(user_id)
    if user_id not in user_preferences:
        user_preferences[str(user_id)] = {}
    return user_preferences[str(user_id)]


def dump_json(data, file: typing.IO):
    file.seek(0)
    file.truncate(0)
    json.dump(data, file)
    file.flush()


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


def get_all_members(ctx):
    all_users = []
    for current_user in ctx.message.guild.members:
        if (current_user.status != "offline") & (
                current_user.status != "busy") & (
                not current_user.bot) & (
                not trapped(current_user.mention)):
            all_users.append(current_user)
    return all_users


def trapped(user):
    if type(user) is str:
        for current_user in trapped_users:
            if user == current_user["user_mention"]:
                return True
    return False


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
