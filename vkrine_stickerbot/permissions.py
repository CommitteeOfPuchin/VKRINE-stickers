import os
import json
import vkrine_stickerbot.utils as utils


class Permissions(object):
    def __init__(self, bot):
        self.__bot__ = bot
        self.__permissions__ = self.load_permissions()

    def reload(self):
        self.__permissions__ = self.load_permissions()

    def load_permissions(self):
        filepath = self.__bot__.runtime() + "/permissions.json"
        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, "r") as file:
                return json.load(file)
        else:
            return __create_default_permissions__(filepath)

    def __create_default_permissions__(self, filepath):
        permissions = {"@owner": [], "@admin": ["command.locale.chat"], "@member": ["command.locale", "command.locale.personal", "command.locale.list",
                                                                                    "command.echo", "command.help"], "@private": ["command.help", "command.locale.list", "command.locale", "command.echo"]}
        with open(filepath, "w") as file:
            json.dump(permissions, file, indent=4)
        return permissions

    def save_permissions(self):
        filepath = self.__bot__.runtime() + "/permissions.json"
        with open(filepath, "w") as file:
            json.dump(self.__permissions__, file, indent=4)

    def have_permission(self, event, permission):
        members = self.__bot__.vk().messages.getConversationMembers(
            peer_id=event.peer_id)["items"]
        member = utils.find_member(members, event.user_id)
        if event.peer_id < 2000000000:
            if utils.in_level_list(self.__permissions__["@private"], permission):
                return True
        else:
            if utils.member_is_admin(member, is_owner=True):
                if utils.in_level_list(self.__permissions__["@owner"], permission):
                    return True
            if utils.member_is_admin(member):
                if utils.in_level_list(self.__permissions__["@admin"], permission):
                    return True
            if utils.in_level_list(self.__permissions__["@member"], permission):
                return True
        chat_id = str(event.peer_id)
        user_id = str(event.user_id)
        if chat_id in self.__permissions__:
            if user_id in self.__permissions__:
                if utils.in_level_list(self.__permissions__[chat_id][user_id], permission):
                    return True
        if user_id in self.__permissions__:
            if utils.in_level_list(self.__permissions__[user_id], permission):
                return True
