from discord.ext import commands
from discord.ext.commands import Context, MissingRequiredArgument, BadArgument
from globals import *
import typing
import inspect
import itertools
from enum import Enum
from jsons import dump_json, user_preferences_json, PreferencesEncoder


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


def get_user_prefs(user_id: typing.Union[int, str]):
    user_id = str(user_id)
    prefs = user_preferences[str(user_id)] if user_id in user_preferences else {}
    if "pronouns" not in prefs:
        prefs["pronouns"] = Pronoun.THEY.value
    if "blacklist" not in prefs:
        prefs["blacklist"] = set()
    return prefs


def set_user_prefs(user_id: typing.Union[int, str], prefs: dict):
    user_preferences[str(user_id)] = prefs


def save_user_prefs():
    dump_json(user_preferences, user_preferences_json, cls=PreferencesEncoder)


class Preferences(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefs", invoke_without_command=True)
    async def preferences(self, ctx: Context):
        pass

    @preferences.command()
    async def pronouns(self, ctx: Context,
                       they: typing.Union[Pronoun, str] = None,
                       them: str = None, their: str = None, theirs: str = None, themself: str = None):
        # display pronouns
        if they is None:
            pronouns = get_user_prefs(ctx.author.id)["pronouns"]
            await ctx.message.channel.send("Pronouns: {they}/{them}/{their}/{theirs}/{themself}"
                                           .format(**pronouns))
            return
        # set pronouns
        they_str = they if isinstance(they, str) else they.name.lower()
        # all pronouns
        if themself is not None:
            pronouns = {"they": they_str,
                        "them": them,
                        "their": their,
                        "theirs": theirs,
                        "themself": themself}
        # only "they"
        else:
            # make sure that it was only "they" that was specified
            if them is not None:
                # find the offending empty parameter
                passed_args = inspect.getargvalues(inspect.currentframe()).locals
                iterator = iter(inspect.signature(Preferences.pronouns.callback).parameters.items())
                # iterate from "their" until end
                for name, param in itertools.islice(iterator, 4, None):
                    if passed_args[name] is None:
                        raise MissingRequiredArgument(param)
                raise MissingRequiredArgument(inspect.signature(Preferences.pronouns.callback).parameters["themself"])
            else:
                # is valid pronoun
                if not isinstance(they, Pronoun):
                    raise BadArgument("Pronoun \"{}\" is not a valid preset.".format(they))
                pronouns = they.value
        prefs = get_user_prefs(ctx.author.id)
        prefs["pronouns"] = pronouns
        set_user_prefs(ctx.author.id, prefs)
        save_user_prefs()
        await ctx.message.channel.send("Preferences updated.")

    @preferences.group(invoke_without_command=True)
    async def blacklist(self, ctx: Context):
        prefs = get_user_prefs(ctx.author.id)
        tags: typing.Set[str] = prefs["blacklist"]
        blacklist: str = ", ".join(sorted(tags))
        if blacklist == "":
            await ctx.message.channel.send("Blacklist empty.")
        else:
            await ctx.message.channel.send("Blacklist: " + blacklist)

    @blacklist.command(name="add")
    async def blacklist_add(self, ctx: Context, *args: str):
        prefs = get_user_prefs(ctx.author.id)
        tags: typing.Set[str] = prefs["blacklist"]
        tags.update(args)
        set_user_prefs(ctx.author.id, prefs)
        save_user_prefs()
        await ctx.message.channel.send("Preferences updated.")

    @blacklist.command(name="remove")
    async def blacklist_remove(self, ctx: Context, *args: str):
        prefs = get_user_prefs(ctx.author.id)
        tags: typing.Set[str] = prefs["blacklist"]
        tags.difference_update(args)
        set_user_prefs(ctx.author.id, prefs)
        save_user_prefs()
        await ctx.message.channel.send("Preferences updated.")
