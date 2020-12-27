from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkApi
from requests.exceptions import ReadTimeout
import os
import vkrine_stickerbot.utils as utils
import time
from vkrine_stickerbot.eventlistener import ChatLogger

class StickerBot(object):
    def __init__(self, runtime="runtime", prefix="/"):
        utils.init_runtime(runtime)
        self.__token__ = utils.load_token(runtime)
        self.__should_stop__ = False
        self.__session__ = VkApi(token=self.__token__)
        self.__vk__ = self.__session__.get_api()
        self.__listening__ = False
        self.__prefix__ = prefix
        self.__chat_logger__ = ChatLogger()
        self.__user__ = self.__vk__.users.get(fields="domain")[0]
        print("Выполнен вход под аккаунтом @id{} ({} {})".format(self.__user__['id'], self.__user__['first_name'], self.__user__['last_name']))

    def run(self):
        reconnect_count = 0
        poll = VkLongPoll(self.__session__, wait=1)
        self.__listening__ = True
        while not self.__should_stop__:
            try:
                if self.__listening__:
                    for event in poll.listen():
                        if self.__should_stop__:
                            break
                        self.__on_event__(event)
                else:
                    if utils.check_connection(r'https://vk.com'):
                        print("Соединение восстановлено")
                        self.__listening__ = True
                        reconnect_count = 0
                        poll = VkLongPoll(self.__session__)
                    else:
                        if reconnect_count >= 60:
                            print("Невозможно восстановить соединение")
                            self.__should_stop__ = True
                        else:
                            reconnect_count += 1
                            print("Потеряно соединение, попытка восстановить номер {}".format(reconnect_count))
                            time.sleep(30)
            except ReadTimeout:
                self.__listening__ = False

    def __on_event__(self, event):
        if event.type == VkEventType.MESSAGE_NEW:
            self.__chat_logger__.on_event(event, self)
            if event.text == "stop":
                self.__should_stop__ = True
            if event.text.startswith("echo "):
                self.send_message(event.peer_id, text=event.text[5:])

    def stop(self):
        self.__should_stop__ = True

    def vk(self):
        return self.__vk__

    def send_message(self, peer_id, text=None, attachments=None):
        self.__vk__.messages.send(peer_id=peer_id, message=text, attachment=attachments, random_id=int(time.time()*1000))

    def get_prefix(self):
        return self.__prefix__
    
    def get_id(self):
        return self.__user__["id"]
    
    def get_domain(self):
        return self.__user__["domain"]