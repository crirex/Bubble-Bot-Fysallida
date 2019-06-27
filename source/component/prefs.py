from discord.ext import commands
from discord.ext.commands import Context, MissingRequiredArgument, Converter, BadArgument
from globals import *
import typing
import inspect
import itertools
from enum import Enum


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


class _Pronoun(Converter):
    async def convert(self, ctx, argument: str):
        return Pronoun[argument.upper()]


def get_user_prefs(user_id):
    user_id = str(user_id)
    prefs = user_preferences[str(user_id)] if user_id in user_preferences else {}
    if "pronouns" not in prefs:
        prefs["pronouns"] = Pronoun.THEY.value
    return prefs


class Preferences(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefs", invoke_without_command=True)
    async def preferences(self, ctx: Context):
        pass

    @preferences.command()
    async def pronouns(self, ctx: Context,
                       they: typing.Union[Pronoun, _Pronoun, str],  # Pronoun can't get converted but _Pronoun does it
                       them: str = None, their: str = None, theirs: str = None, themself: str = None):
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
                if not isinstance(they, Pronoun):
                    raise BadArgument("Pronoun \"{}\" is not a valid preset.".format(they))
                pronouns = they.value
        get_user_prefs(ctx.author.id)["pronouns"] = pronouns
        dump_json(user_preferences, user_preferences_json)
        await ctx.message.channel.send("Preferences updated.")
