from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkApi
from requests.exceptions import ReadTimeout
import os
import vkrine_stickerbot.utils as utils
import time
from vkrine_stickerbot.eventlistener import ChatLogger
from vkrine_stickerbot.permissions import Permissions
from vkrine_stickerbot.l10n import L10n
from vkrine_stickerbot.commandhandler import CommandHandler


class StickerBot(object):
    def __init__(self, runtime="runtime", prefix="/"):
        utils.init_runtime(runtime)
        self.__token__ = utils.load_token(runtime)
        self.__should_stop__ = False
        self.__runtime__ = runtime
        self.__session__ = VkApi(token=self.__token__)
        self.__vk__ = self.__session__.get_api()
        self.__listening__ = False
        self.__prefix__ = prefix
        self.__permissions__ = Permissions(self)
        self.__l10n__ = L10n(self)
        self.__command_handler__ = CommandHandler(self)
        self.__chat_logger__ = ChatLogger()
        self.__user__ = self.__vk__.users.get(fields="domain")[0]
        print("Выполнен вход под аккаунтом @id{} ({} {})".format(self.__user__[
              'id'], self.__user__['first_name'], self.__user__['last_name']))

    def runtime(self):
        return self.__runtime__

    def run(self):
        while not self.__should_stop__:
            try:
                poll = VkLongPoll(self.__session__)
                for event in poll.listen():
                    if self.__should_stop__:
                        break
                    self.__on_event__(event)
            except ReadTimeout:
                reconnect_count = 0
                while not utils.check_connection(r'https://vk.com') and reconnect_count < 60:
                    reconnect_count += 1
                    print("Потеряно соединение, попытка восстановить номер {}".format(
                        reconnect_count))
                    time.sleep(30)
                if reconnect_count == 60:
                    print("Невозможно восстановить соединение")
                    self.stop()
                else:
                    print("Соединение восстановлено")
        self.__permissions__.save_permissions()
        self.__l10n__.save_settings()

    def __on_event__(self, event):
        self.__chat_logger__.on_event(event, self)
        self.__command_handler__.on_event(event, self)

    def stop(self):
        self.__should_stop__ = True

    def vk(self):
        return self.__vk__

    def command_handler(self):
        return self.__command_handler__

    def send_message(self, peer_id, text=None, attachment=None):
        if text and not attachment:
            self.__vk__.messages.send(
                peer_id=peer_id, message=text, random_id=int(time.time()*1000))
        elif attachment and not text:
            self.__vk__.messages.send(
                peer_id=peer_id, attachment=attachment, random_id=int(time.time()*1000))
        elif attachment and text:
            self.__vk__.messages.send(
                peer_id=peer_id, message=text, attachment=attachment, random_id=int(time.time()*1000))

    def get_prefix(self):
        return self.__prefix__

    def get_id(self):
        return self.__user__["id"]

    def get_domain(self):
        return self.__user__["domain"]

    def l10n(self):
        return self.__l10n__

    def permissions(self):
        return self.__permissions__
