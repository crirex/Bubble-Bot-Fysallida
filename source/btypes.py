import random
from enum import Enum
from typing import Set, List, Union, Dict

__all__ = [
    "BubbleEnum",
    "BubbleColor",
    "BubbleType",
    "BubbleTag",
    "BubblePlay",
    "Config",
    "TrappingText",
    "BubbleTrap",
    "Pronoun",
    "UserPreferences",
]


class BubbleEnum(Enum):
    # allow for discord.py to convert a string to this enum
    @classmethod
    def convert_(cls, argument: str):
        return cls[argument.upper()]

    # noinspection PyUnusedLocal
    @classmethod
    async def convert(cls, ctx, argument: str):
        return cls.convert_(argument)

    @classmethod
    def random(cls):
        return random.choice(cls)


class BubblePlay(BubbleEnum):
    TRAP = "trap"
    SQUISH = "squish"
    SIT = "sit"


class BubbleType(BubbleEnum):
    SOAP = "soap"
    RUBBER = "rubber"
    GUM = "gum"
    PLASTIC = "plastic"
    GLASS = "glass"
    MAGIC = "magic"


class BubbleColor(BubbleEnum):
    ORANGE = "orange"
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    YELLOW = "yellow"
    WHITE = "white"
    PINK = "pink"
    PURPLE = "purple"
    TEAL = "teal"
    BLACK = "black"


# TODO tags
class BubbleTag(BubbleEnum):
    pass


class Config:
    def __init__(self, token: str, prefix: str, owner: int, yt_key: str):
        self.token = token
        self.prefix = prefix
        self.owner = owner
        self.yt_key = yt_key


class TrappingText:
    def __init__(self, text: str, play_type: str, bubble_type: str,
                 tags: List[str] = tuple()):
        self.text: str = text
        self.play_type: BubblePlay = BubblePlay.convert_(play_type)
        self.bubble_type: BubbleType = BubbleType.convert_(bubble_type)
        self.tags: Set[BubbleTag] = {t for t in [BubbleTag.convert_(tag) for tag in tags] if t is not None}


class BubbleTrap:
    def __init__(self, user: int,
                 bubble_play: Union[BubblePlay, str],
                 bubble_type: Union[BubbleType, str],
                 bubble_color: Union[BubbleColor, str],
                 time: float, channel: int, tries: int
                 ):
        self.user = user
        self.bubble_play: BubblePlay =\
            bubble_play if isinstance(bubble_play, BubblePlay) else BubblePlay.convert_(bubble_play)
        self.bubble_type: BubbleType =\
            bubble_type if isinstance(bubble_type, BubbleType) else BubbleType.convert_(bubble_type)
        self.bubble_color: BubbleColor =\
            bubble_color if isinstance(bubble_color, BubbleColor) else BubbleColor.convert_(bubble_color)
        self.time = time
        self.channel = channel
        self.tries = tries


class Pronoun(Enum):
    HE = {
        "they": "he",
        "them": "him",
        "their": "his",
        "theirs": "his",
        "themself": "himself"
    }
    SHE = {
        "they": "she",
        "them": "her",
        "their": "her",
        "theirs": "hers",
        "themself": "herself"
    }
    THEY = {
        "they": "they",
        "them": "them",
        "their": "their",
        "theirs": "theirs",
        "themself": "themself"
    }

    # allow for discord.py to convert a string to this enum
    # noinspection PyUnusedLocal
    @classmethod
    async def convert(cls, ctx, argument: str):
        return cls[argument.upper()]


class UserPreferences:
    def __init__(self,
                 pronouns: Dict[str, str] = None,
                 blacklist: List[str] = tuple(),
                 ping: bool = True,
                 tz: str = "",
                 miltime: bool = True,
                 ):
        self.pronouns = pronouns if pronouns is not None else Pronoun.THEY.value
        black_play: Set[BubblePlay] = {BubblePlay.convert_(value) for value in blacklist}
        black_type: Set[BubbleType] = {BubbleType.convert_(value) for value in blacklist}
        black_color: Set[BubbleColor] = {BubbleColor.convert_(value) for value in blacklist}
        black_tag: Set[BubbleTag] = {BubbleTag.convert_(value) for value in blacklist}
        self.blacklist = black_play | black_type | black_color | black_tag
        try:
            # noinspection PyTypeChecker
            self.blacklist.remove(None)
        except KeyError:
            pass
        self.ping = ping
        self.tz = tz
        self.miltime = miltime
