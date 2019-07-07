import json
from json import JSONDecodeError, JSONEncoder, JSONDecoder
from typing import List, Dict

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


def dump_json(obj, fp, *, skipkeys=False, ensure_ascii=True, check_circular=True,
              allow_nan=True, cls=None, indent=None, separators=None,
              default=None, sort_keys=False, **kw):
    fp.seek(0)
    fp.truncate(0)
    json.dump(obj, fp, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
              allow_nan=allow_nan, cls=cls, indent=indent, separators=separators,
              default=default, sort_keys=sort_keys, **kw)
    fp.flush()
