from datetime import datetime
from typing import Union

from discord.ext import commands
from discord.ext.commands import Context, Bot
from discord import Member, User

from btypes import UserPreferences
from utils import me, get_timezone
from .prefs import Preferences


def time_fmt(prefs: UserPreferences):
    return "%H:%M" if prefs.miltime else "%I:%M %p"


class Time(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.preferences: Preferences = self.bot.get_cog("Preferences")

    @commands.command(name='time',
                      pass_context=True)
    async def show_time(self, ctx: Context, user: Union[Member, User, me, None]):
        if user is None:
            user = ctx.message.author
        user_prefs = await self.preferences.get_user_prefs(user.id)
        author_prefs = await self.preferences.get_user_prefs(ctx.author.id)
        if not user_prefs.tz:
            await ctx.send("User has no timezone set.")
        else:
            tz = get_timezone(user_prefs.tz)
            dt = datetime.now(tz)
            await ctx.send(dt.strftime(time_fmt(author_prefs)) + " " + tz.tzname(dt))

    @commands.command(name='time2',
                      pass_context=True)
    async def secret_time(self, ctx: Context):
        """This is the hardcoded version for the both of us only"""
        author_prefs = await self.preferences.get_user_prefs(ctx.author.id)
        await ctx.send(
            "Autumn time: " + datetime.now(get_timezone("America/New_York")).strftime(time_fmt(author_prefs)) + "\n" +
            "Crirex time: " + datetime.now(get_timezone("Europe/Bucharest")).strftime(time_fmt(author_prefs))
        )

    # Eventually move into the help command
    @commands.command(name='zones',
                      pass_context=True)
    async def show_zones(self, ctx: Context):
        await ctx.send("Visit https://askgeo.com/#map and select your location on the map.\n"
                       "Then scroll down and find the value associated with the key \"TimeZoneId\".")
