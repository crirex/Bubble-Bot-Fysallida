import asyncio
import json
from json import JSONDecodeError, JSONEncoder, JSONDecoder
from typing import List, Dict

from discord.ext import commands, tasks
from discord.ext.commands import Bot

from btypes import *


class Encoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, (BubbleTrap, UserPreferences)):
            diction = obj.__dict__
            return diction
        if isinstance(obj, BubbleEnum):
            return obj.value
        return super().default(obj)


class ConfigDecoder(JSONDecoder):
    def decode(self, s, _w=json.decoder.WHITESPACE.match):
        return Config(**(super().decode(s, _w)))


class TextDecoder(JSONDecoder):
    def decode(self, s, _w=json.decoder.WHITESPACE.match):
        return [TrappingText(**d) for d in super().decode(s, _w)]


class BubbleDecoder(JSONDecoder):
    def decode(self, s, _w=json.decoder.WHITESPACE.match):
        return [BubbleTrap(**d) for d in super().decode(s, _w)]


class PreferencesDecoder(JSONDecoder):
    def decode(self, s, _w=json.decoder.WHITESPACE.match):
        return {k: UserPreferences(**v) for k, v in super().decode(s, _w).items()}


class Writeback(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.trapped_dirty = False
        self.prefs_dirty = False
        self.trapped_lock = asyncio.Lock(loop=bot.loop)
        self.prefs_lock = asyncio.Lock(loop=bot.loop)
        self.writeback.start()

    def cog_unload(self):
        self.writeback.cancel()

    @staticmethod
    def dump_json(obj, fp, *, skipkeys=False, ensure_ascii=True, check_circular=True,
                  allow_nan=True, cls=None, indent=None, separators=None,
                  default=None, sort_keys=False, **kw):
        fp.seek(0)
        fp.truncate(0)
        json.dump(obj, fp, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                  allow_nan=allow_nan, cls=cls, indent=indent, separators=separators,
                  default=default, sort_keys=sort_keys, **kw)
        fp.flush()

    def sync_trapped_users(self):
        assert self.trapped_lock.locked(), "Trapped users lock not held"
        self.trapped_dirty = True

    def sync_user_preferences(self):
        assert self.prefs_lock.locked(), "User preferences lock not held"
        self.prefs_dirty = True

    async def write_trapped_users(self):
        assert self.trapped_lock.locked(), "Trapped users lock not held"
        # print("Writing trapped users")
        self.dump_json(trapped_users, trapped_users_json, cls=Encoder)
        self.trapped_dirty = False

    async def write_user_preferences(self):
        assert self.prefs_lock.locked(), "User preferences lock not held"
        # print("Writing preferences")
        self.dump_json(user_preferences, user_preferences_json, cls=Encoder)
        self.prefs_dirty = False

    # noinspection PyCallingNonCallable
    @tasks.loop(seconds=5)
    async def writeback(self):
        # print("writeback()")
        coros = []
        await self.trapped_lock.acquire()
        await self.prefs_lock.acquire()
        # Trapped users
        if self.trapped_dirty:
            coros.append(self.write_trapped_users())
        else:
            self.trapped_lock.release()
        # User prefs
        if self.prefs_dirty:
            coros.append(self.write_user_preferences())
        else:
            self.prefs_lock.release()
        # Do the concurrent writebacks
        try:
            await asyncio.gather(*coros, loop=self.bot.loop)
        finally:
            if self.trapped_lock.locked():
                self.trapped_lock.release()
            if self.prefs_lock.locked():
                self.prefs_lock.release()

    @writeback.before_loop
    async def writeback_before(self):
        await self.bot.wait_until_ready()


with open("config.json", "r") as config_json:
    config: Config = json.load(config_json, cls=ConfigDecoder)
with open("TrappingText.json", "r") as trapping_text_json:
    trapping_text: List[TrappingText] = json.load(trapping_text_json, cls=TextDecoder)
try:
    with open("TrappedUsers.json", "r") as trapped_users_json:
        trapped_users = json.load(trapped_users_json, cls=BubbleDecoder)
except (JSONDecodeError, IOError):
    trapped_users: List[BubbleTrap] = []
trapped_users_json = open("TrappedUsers.json", "r+")
try:
    with open("UserPreferences.json", "r") as user_preferences_json:
        user_preferences: Dict[str, UserPreferences] = json.load(user_preferences_json, cls=PreferencesDecoder)
except (JSONDecodeError, IOError):
    user_preferences = {}
user_preferences_json = open("UserPreferences.json", "r+")
