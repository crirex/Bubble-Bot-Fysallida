from string import Formatter as oldFormatter


# https://stackoverflow.com/a/46160537
class Formatter(oldFormatter):
    def get_value(self, key, args, kwargs):
        """Accept literal strings"""
        if isinstance(key, str):
            key = str(key)
            if (key.startswith("\"") and key.endswith("\"")) or (key.startswith("'") and key.endswith("'")):
                key = key[1:-1]
                # verb conjugations
                # ex. He/they {'has|v|have'}
                if key.find("|v|") != -1:
                    if "they" in kwargs:
                        verbs = key.split("|v|")
                        if kwargs["they"] == "they" or kwargs["they"] == "you":
                            return verbs[1]
                        else:
                            return verbs[0]
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
