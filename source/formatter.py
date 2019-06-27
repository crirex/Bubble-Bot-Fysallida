import re
from string import Formatter as oldFormatter


def import_pronouns(diction: dict, *pronouns: dict):
    """Updates diction with multiple pronoun sets with keys "they0", "they1", ...
    :param diction:
    :param pronouns:
    :return: None
    """
    for p in pronouns:
        diction.update({str(kv[0]) + str(i): kv[1] for i, kv in enumerate(p.items())})


# https://stackoverflow.com/a/46160537
class Formatter(oldFormatter):
    def get_value(self, key, args, kwargs):
        """Accept literal strings, but no ! or :"""
        if isinstance(key, str):
            key = str(key)
            # string literals and option literals
            if (key.startswith("\"") and key.endswith("\"")) or (key.startswith("'") and key.endswith("'")):
                key = key[1:-1]
                # verb conjugations
                # ex. He/they {'has|v|have'}
                conj_match = re.match(r"^(.*)\|v(\d*)\|(.*)$", key, re.DOTALL)
                if conj_match is not None:
                    singular, index, plural = conj_match.groups()
                    if index == "":
                        if "they" in kwargs:
                            if kwargs["they"] == "they" or kwargs["they"] == "you":
                                return plural
                            else:
                                return singular
                        raise ValueError("Verb conjugation requires \"they\" key in kwargs")
                    else:
                        index = str(int(index))
                        if "they"+index in kwargs:
                            if kwargs["they"+index] == "they" or kwargs["they"+index] == "you":
                                return plural
                            else:
                                return singular
                        raise ValueError("Verb conjugation requires \"they{0}\" key in kwargs".format(index))
                return key
        return super().get_value(key, args, kwargs)

    def convert_field(self, value, conversion):
        """ Extend conversion symbols
        Additional symbols:
        * l: convert to string and lowercase
        * u: convert to string and uppercase
        * c: convert to string and capitalize
        * v: conjugates a verb

        Default symbols:
        * s: convert with str()
        * r: convert with repr()
        * a: convert with ascii()
        """

        if conversion == "u":
            return str(value).upper()
        elif conversion == "l":
            return str(value).lower()
        elif conversion == "c":
            return str(value).capitalize()
        # default conversion
        return super().convert_field(value, conversion)


formatter = Formatter()
