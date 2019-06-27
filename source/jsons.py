import json
from json import JSONDecodeError, JSONEncoder, JSONDecoder


class PreferencesEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


class PreferencesDecoder(JSONDecoder):
    def decode(self, s, _w=json.decoder.WHITESPACE.match):
        obj: dict = super().decode(s, _w)
        for user_id in obj.keys():
            prefs = obj[user_id]
            if "blacklist" in prefs:
                prefs["blacklist"] = set(prefs["blacklist"])
        return obj


with open("config.json", "r") as config_json:
    config = json.load(config_json)
with open("TrappingText.json", "r") as trapping_text_json:
    trapping_text = json.load(trapping_text_json)
try:
    with open("TrappedUsers.json", "r") as trapped_users_json:
        trapped_users = json.load(trapped_users_json)
except (JSONDecodeError, IOError):
    trapped_users = []
trapped_users_json = open("TrappedUsers.json", "w+")
try:
    with open("UserPreferences.json", "r") as user_preferences_json:
        user_preferences = json.load(user_preferences_json, cls=PreferencesDecoder)
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
