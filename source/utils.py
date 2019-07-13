from datetime import tzinfo
from typing import Union

import dateutil.zoneinfo
from discord import Member, User
from discord.ext import commands


# Gets an IANA timezone
def get_timezone(zone: str) -> tzinfo:
    return dateutil.zoneinfo.get_zonefile_instance().get(zone, default=None)


# Discord.py converter that maps the string "me" to the user who sent the message
# noinspection PyPep8Naming
class me(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> Union[Member, User]:
        if argument.lower() == "me":
            return ctx.author
        else:
            raise commands.BadArgument("\"{}\" could not be recognized as a valid self keyword.".format(argument))
