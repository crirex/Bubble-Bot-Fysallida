import random
import time
# noinspection PyUnresolvedReferences
from jsons import config, trapping_text, trapped_users, user_preferences

start_time = time.time()
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
