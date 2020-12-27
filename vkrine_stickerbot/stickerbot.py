from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkApi
from requests.exceptions import ReadTimeout
import os
import vkrine_stickerbot.utils as utils
import time

class StickerBot:
    def __init__(self, runtime="runtime"):
        utils.init_runtime(runtime)
        self.__token__ = utils.load_token(runtime)
        self.__should_stop__ = False
        self.__session__ = VkApi(token=self.__token__)
        self.__vk__ = self.__session__.get_api()
        self.__listening__ = False

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
            print(event.text)
            if event.text == "stop":
                self.__should_stop__ = True

    def stop(self):
        self.__should_stop__ = True
