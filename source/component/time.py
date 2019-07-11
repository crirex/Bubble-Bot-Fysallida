from datetime import datetime
from pytz import timezone, all_timezones_set, utc

from typing import Union

from discord.ext import commands
from discord.ext.commands import Context
from discord import Member, User, TextChannel


# noinspection PyPep8Naming
class me(commands.Converter):
    async def convert(self, ctx: Context, argument: str) -> Union[Member, User]:
        if argument.lower() == "me":
            return ctx.author
        else:
            raise BadArgument("\"{}\" could not be recognized as a valid self keyword.".format(argument))


def get_time_by_country(country: str):
    utc_dt = utc.localize(datetime.utcfromtimestamp(int(datetime.now(tz=timezone("UTC")).timestamp())))
    country_timezone = timezone(country)
    time_format = '%H:%M:%S'
    # time_format = '%Y-%m-%d %H:%M:%S %Z%z'  # Use this format for full info
    time = utc_dt.astimezone(country_timezone)
    return time.strftime(time_format)


def get_all_available_timezones():
    return list(all_timezones_set)


def search_for_timezone(search_argument: str):
    return [current_timezone for current_timezone in get_all_available_timezones()
            if search_argument in current_timezone]


def is_valid_timezone(zone: str):
    for current_timezone in get_all_available_timezones():
        if zone == current_timezone:
            return True
    return False


class Time(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='time',
                      pass_context=True)
    async def show_time(self, ctx, user: Union[Member, User, me, None]):
        ''' This should be the general code to be modified and used
        if user is None:
            user = ctx.message.author
        user_zone = preferences of user
        await ctx.message.channel.send(get_time_by_country(user_zone))
        '''
        # This is the hardcoded version for the both of us only that works with strings
        # (i don't it too complicated for something hardcoded)
        await ctx.message.channel.send("Autumn time: " + get_time_by_country('America/New_York') + '\n' +
                                       "Crirex time: " + get_time_by_country('Europe/Bucharest'))

    # Leaves the voice channel
    @commands.command(name='searchZones',
                      pass_context=True,
                      aliases=['searchzones'])
    async def show_options(self, ctx, argument=None):
        if argument is None:
            options = get_all_available_timezones()
        else:
            options = search_for_timezone(argument)
        await ctx.message.channel.send(print(', '.join(options)))
