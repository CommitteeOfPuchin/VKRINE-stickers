
import datetime
import vkrine_stickerbot.utils as utils

class EventListener(object):
    def on_event(self, event, bot):
        pass

class MessageListener(EventListener):
    def __init__(self, call_itself=False):
        self.__call_itself__ = call_itself

    def __can_call__(self, event, bot):
        return event.user_id != bot.get_id() or self.__call_itself__

    def on_event(self, event, bot):
        if self.__can_call__(event, bot):
            self._on_message_(event, bot)
    
    def _on_message_(self, event, bot):
        pass

class ChatLogger(MessageListener):
    def _on_message_(self, event, bot):
        user = bot.vk().users.get(user_ids=event.user_id)[0]
        peer = "{} ({}) | ".format(event.peer_id, bot.vk().messages.getConversationsById(peer_ids=event.peer_id)['items'][0]['chat_settings']['title'])
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        print("{}: {}@id{} ({} {}): {}".format(now, peer, user['id'], user['first_name'], user['last_name'], utils.decode_text(event.text)))

