from discord.ext import commands
from discord.ext.commands import Context
from globals import *


def get_user_prefs(user_id):
    user_id = str(user_id)
    prefs = user_preferences[str(user_id)] if user_id in user_preferences else {}
    if "pronouns" not in prefs:
        prefs["pronouns"] = {
            "they": "they",
            "them": "them",
            "their": "their",
            "theirs": "theirs",
            "themself": "themself"
        }
    return prefs


class Preferences(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefs", invoke_without_command=True)
    async def preferences(self, ctx: Context):
        pass

    @preferences.command()
    async def pronouns(self, ctx: Context, they: str, them: str, their: str, theirs: str, themself: str):
        get_user_prefs(ctx.author.id)["pronouns"] = {"they": they,
                                                     "them": them,
                                                     "their": their,
                                                     "theirs": theirs,
                                                     "themself": themself}
        dump_json(user_preferences, user_preferences_json)
        await ctx.message.channel.send("Preferences updated.")