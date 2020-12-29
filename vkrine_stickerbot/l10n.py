import os
import json


class L10n(object):
    def __init__(self, bot):
        self.__bot__ = bot
        self.__base_locale__ = {}
        self.__locales__ = {}
        self.__settings__ = {}
        self.load_localization()

    def reload(self):
        self.load_localization()

    def load_localization(self):
        filepath = self.__bot__.runtime() + "/l10n.json"
        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, "r") as file:
                self.__settings__ = json.load(file)
        else:
            self.__settings__ = self.__create_default_settings__(filepath)
        dirpath = "locales"
        for filename in os.listdir(dirpath):
            filepath = "{}/{}".format(dirpath, filename)
            if (os.path.isfile(filepath)):
                name = os.path.splitext(filename)[0]
                with open(filepath, "r") as file:
                    self.__locales__[name] = json.load(file)

    def save_settings(self):
        filepath = self.__bot__.runtime() + "/l10n.json"
        with open(filepath, "w") as file:
            json.dump(self.__settings__, file, indent=4)

    def __create_default_settings__(self, filepath):
        settings = {"@main": ["en_US", "Global locale"]}
        with open(filepath, "w") as file:
            json.dump(settings, file, indent=4)
        return settings

    def translate_list(self, peer_id, user_id, key, *args, **kwargs):
        result = []
        locale = self.__locales__[self.get_locale(peer_id, user_id)]
        if key in locale["keys"]:
            for element in locale["keys"][key]:
                result.append(element.format(*args, **kwargs))
        elif key in self.get_default_locale():
            locale = self.get_default_locale()
            for element in locale["keys"][key]:
                result.append(element.format(*args, **kwargs))
        return result

    def translate_default(self, key, *args, **kwargs):
        return self.translate(0, 0, key, *args, **kwargs)

    def translate_list_default(self, key, *args, **kwargs):
        return self.translate_list(0, 0, key, *args, **kwargs)

    def translate(self, peer_id, user_id, key, *args, **kwargs):
        result = key
        locale = self.__locales__[self.get_locale(peer_id, user_id)]
        if key in locale["keys"]:
            result = locale["keys"][key].format(*args, **kwargs)
        elif key in self.get_default_locale()["keys"]:
            locale = self.get_default_locale()
            result = locale["keys"][key].format(*args, **kwargs)
        return result

    def reset_locale(self, target):
        if target != "@main":
            del self.__settings__[target]
        self.save_settings()

    def set_locale(self, target, locale):
        if locale in self.__settings__:
            self.__settings__[target][0] = locale
        else:
            self.__settings__[target] = [locale]
        self.save_settings()

    def get_target(self, value):
        if value in self.__settings__:
            return value
        else:
            return "@main"

    def get_locale_by_target(self, target):
        return self.__settings__[target][0]

    def has_locale(self, locale):
        return locale in self.__locales__

    def get_default_locale(self):
        return self.__locales__[self.__settings__["@main"][0]]

    def get_locale(self, peer_id, user_id):
        target = self.__get_target__(peer_id, user_id)
        return self.__settings__[target][0]

    def __get_target__(self, peer_id, user_id):
        if str(user_id) in self.__settings__:
            return str(user_id)
        if str(peer_id) in self.__settings__:
            return str(peer_id)
        return "@main"

    def get_locales(self):
        return self.__locales__.keys()
