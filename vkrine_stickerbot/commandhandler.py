from vkrine_stickerbot.eventlistener import MessageListener
import vkrine_stickerbot.utils as utils
import shlex
import vkrine_stickerbot.exceptions as exceptions
import sys
import re
import traceback


class CommandHandler(MessageListener):
    def __init__(self, bot):
        super().__init__()
        self.__bot__ = bot
        self.__commands__ = self.__load_commands__()

    def __load_commands__(self):
        return [CommandEcho(), CommandStop(), CommandReload(), CommandLocale(), CommandHelp()]

    def commands(self):
        return self.__commands__

    def _on_message_(self, event, bot):
        text = utils.decode_text(event.text)
        command_raw = utils.try_remove_prefix(text, bot)
        if len(command_raw) != len(text):
            command_raw = command_raw.split()
            try:
                command = self.get_command(event, command_raw[0])
                if bot.permissions().have_permission(event, command.get_permission()):
                    line = " ".join(command_raw[1:])
                    command.run(event, bot, utils.decode_quot(
                        line), shlex.split(line))
                    return True
                else:
                    bot.send_message(event.peer_id, bot.l10n().translate(
                        event.peer_id, event.user_id, "commands.generic.permission"))
            except exceptions.WrongUsageException as e:
                message = bot.l10n().translate(event.peer_id, event.user_id, command.get_help())
                bot.send_message(event.peer_id, bot.l10n().translate(
                    event.peer_id, event.user_id, "commands.generic.usage", message))
            except exceptions.CommandException as e:
                bot.send_message(event.peer_id, bot.l10n().translate(
                    event.peer_id, event.user_id, e.get_message(), *e.get_args(), **e.get_kwargs()))
            except Exception as e:
                bot.send_message(event.peer_id, bot.l10n().translate(
                    event.peer_id, event.user_id, "commands.generic.exception", e))
                traceback.print_exc()

    def get_command(self, event, phrase):
        for command in self.__commands__:
            if command.get_name() == phrase:
                return command
            if command.get_aliases_key():
                if phrase in self.__bot__.l10n().translate_list(event.peer_id, event.user_id, command.get_aliases_key()):
                    return command
                if phrase in self.__bot__.l10n().translate_list_default(command.get_aliases_key()):
                    return command
        raise exceptions.CommandNotFoundException(None)


class Command(object):
    def __init__(self, name):
        self.__command_name__ = name

    def get_name(self):
        return self.__command_name__

    def get_aliases_key(self):
        return "commands.{}.aliases".format(self.__command_name__)

    def run(self, event, bot, line, args):
        pass

    def get_permission(self):
        return "command.{}".format(self.__command_name__)

    def get_help(self):
        return "help.{}".format(self.__command_name__)

    def get_help_extended(self):
        return "help.{}.extended".format(self.__command_name__)

    def reply_translated(self, event, bot, key, attachment, *args, **kwargs):
        message = bot.l10n().translate(event.peer_id, event.user_id, key, *args, **kwargs)
        self.reply(event, bot, message, attachment)

    def reply(self, event, bot, text=None, attachment=None):
        bot.send_message(event.peer_id, text, attachment)

    def get_arg_key(self, arg):
        return "commands.{}.{}".format(self.__command_name__, arg)

    def get_arg_permission(self, arg):
        return "command.{}.{}".format(self.__command_name__, arg)


def is_arg(bot, event, arg, key, phrase):
    if arg == phrase:
        return True
    if phrase in bot.l10n().translate_list(event.peer_id, event.user_id, key):
        return True
    if phrase in bot.l10n().translate_list_default(key):
        return True


def have_permission(bot, event, permission):
    if not bot.have_permission(event, permission):
        raise exceptions.CommandException("commands.generic.permission")


def parse_int(bot, arg):
    try:
        return int(arg)
    except ValueError:
        raise exceptions.NumberInvalidException(None, arg)


def parse_int_with_min(bot, arg, min):
    return parse_int_bounded(bot, arg, min, sys.maxint)


def parse_int_bounded(bot, arg, min, max):
    result = parse_int(bot, arg)
    if result > max:
        raise exceptions.NumberInvalidException(
            "commands.generic.num.to_big", arg, max)
    elif result < min:
        raise exceptions.NumberInvalidException(
            "commands.generic.num.to_small", arg, min)
    else:
        return result


def parse_float(bot, arg):
    try:
        f = float(arg)
        f.as_integer_ratio()
        return f
    except ValueError or OverflowError:
        raise exceptions.NumberInvalidException(None, arg)


def parse_float_with_min(bot, arg, min):
    return parse_float_bounded(bot, arg, min, sys.maxint)


def parse_float_bounded(bot, arg, min, max):
    result = parse_float(bot, arg)
    if result > max:
        raise exceptions.NumberInvalidException(
            "commands.generic.float.to_big", arg, max)
    elif result < min:
        raise exceptions.NumberInvalidException(
            "commands.generic.float.to_small", arg, min)
    else:
        return result


def parse_bool(bot, arg):
    if arg != "true" and arg != "1":
        if arg != "false" and arg != "0":
            raise exceptions.CommandException(
                "commands.generic.boolean.invalid", arg)
        else:
            return False
    else:
        return True


def get_user(bot, arg):
    mentioned = re.sub(r'^((\[(\S+?)\|\S+?\])|(@(\S+)( \(\S+?\))?))',
                       r'\3\5', arg, re.IGNORECASE + re.DOTALL)
    if len(mentioned) != len(arg):
        uid = mentioned.split()[0].lower()
    else:
        uid = arg
    users = bot.vk().users.get(user_ids=uid)
    l = len(users)
    if l > 0:
        if l > 1:
            return users
        else:
            return users[0]
    else:
        raise exceptions.UserNotFoundException(None, arg)


class CommandEcho(Command):
    def __init__(self):
        super().__init__("echo")

    def run(self, event, bot, line, args):
        self.reply(event, bot, text=" ".join(args))


class CommandReload(Command):
    def __init__(self):
        super().__init__("reload")

    def run(self, event, bot, line, args):
        bot.permissions().reload()
        bot.l10n().reload()
        self.reply_translated(event, bot, "commands.done", None)


class CommandStop(Command):
    def __init__(self):
        super().__init__("stop")

    def run(self, event, bot, line, args):
        bot.stop()
        self.reply_translated(event, bot, "commands.done", None)


class CommandLocale(Command):
    def __init__(self):
        super().__init__("locale")

    def run(self, event, bot, line, args):
        l = len(args)
        if l == 0:
            raise exceptions.WrongUsageException(None)
        if is_arg(bot, event, "global", self.get_arg_key("global"), args[0]):
            if not bot.permissions().have_permission(event, self.get_arg_permission("global")):
                raise exceptions.CommandException(
                    "commands.generic.permission")
            if l == 2:
                locale = args[1]
                if locale == "default":
                    bot.l10n().set_locale("@main", "en_US")
                    self.reply_translated(event, bot, "commands.done", None)
                elif bot.l10n().has_locale(locale):
                    bot.l10n().set_locale("@main", locale)
                    self.reply_translated(event, bot, "commands.done", None)
                else:
                    self.reply_translated(
                        event, bot, "commands.text.locale.not_found", None, locale)
            elif l == 1:
                locale = bot.l10n().get_default_locale()
                self.reply_translated(
                    event, bot, "commands.text.locale.current", None, locale)
            else:
                raise exceptions.WrongUsageException(None)
        if is_arg(bot, event, "chat", self.get_arg_key("chat"), args[0]):
            if not bot.permissions().have_permission(event, self.get_arg_permission("chat")):
                raise exceptions.CommandException(
                    "commands.generic.permission")
            if l == 2:
                locale = args[1]
                if locale == "default":
                    bot.l10n().reset_locale(str(event.peer_id))
                    self.reply_translated(event, bot, "commands.done", None)
                elif bot.l10n().has_locale(locale):
                    bot.l10n().set_locale(str(event.peer_id), locale)
                    self.reply_translated(event, bot, "commands.done", None)
                else:
                    self.reply_translated(
                        event, bot, "commands.text.locale.not_found", None, locale)
            elif l == 1:
                locale = bot.l10n().get_locale_by_target(
                    bot.l10n().get_target(str(event.peer_id)))
                self.reply_translated(
                    event, bot, "commands.text.locale.current", None, locale)
            else:
                raise exceptions.WrongUsageException(None)
        if is_arg(bot, event, "personal", self.get_arg_key("personal"), args[0]):
            if not bot.permissions().have_permission(event, self.get_arg_permission("personal")):
                raise exceptions.CommandException(
                    "commands.generic.permission")
            if l == 2:
                locale = args[1]
                if locale == "default":
                    bot.l10n().reset_locale(str(event.user_id))
                    self.reply_translated(event, bot, "commands.done", None)
                elif bot.l10n().has_locale(locale):
                    bot.l10n().set_locale(str(event.user_id), locale)
                    self.reply_translated(event, bot, "commands.done", None)
                else:
                    self.reply_translated(
                        event, bot, "commands.text.locale.not_found", None, locale)
            elif l == 1:
                locale = bot.l10n().get_locale_by_target(
                    bot.l10n().get_target(str(event.user_id)))
                self.reply_translated(
                    event, bot, "commands.text.locale.current", None, locale)
            else:
                raise exceptions.WrongUsageException(None)
        if is_arg(bot, event, "list", self.get_arg_key("list"), args[0]):
            if not bot.permissions().have_permission(event, self.get_arg_permission("list")):
                raise exceptions.CommandException(
                    "commands.generic.permission")
            if l == 1:
                locales = bot.l10n().get_locales()
                self.reply_translated(
                    event, bot, "commands.text.locale.list", None, ", ".join(locales))
            else:
                raise exceptions.WrongUsageException(None)


class CommandHelp(Command):
    def __init__(self):
        super().__init__("help")
        self.__pages__ = None

    def __init_pages_lazy__(self, bot):
        if not self.__pages__:
            commands = bot.command_handler().commands()
            self.__pages__ = [commands[i:i+8]
                              for i in range(0, len(commands), 8)]

    def run(self, event, bot, line, args):
        self.__init_pages_lazy__(bot)
        page = 0
        command_name = None
        if len(args) > 0:
            try:
                page = parse_int_bounded(
                    bot, args[0], 0, len(self.__pages__) - 1)
            except exceptions.NumberInvalidException:
                command_name = args[0]
        if command_name:
            command = bot.command_handler().get_command(event, command_name)
            text = bot.l10n().translate(event.peer_id, event.user_id, command.get_help_extended())
            aliases = bot.l10n().translate_list(
                event.peer_id, event.user_id, command.get_aliases_key())
            aliases += bot.l10n().translate_list_default(command.get_aliases_key())
            aliases = "', '".join(aliases)
            if not aliases:
                aliases = bot.l10n().translate(event.peer_id, event.user_id, "commands.none")
            else:
                aliases = "'{}'".format(aliases)
            aliases = bot.l10n().translate(event.peer_id, event.user_id, "help.aliases", aliases)
            self.reply(event, bot, "{}\n\n{}".format(text, aliases))
        else:
            page_data = []
            for command in self.__pages__[page]:
                text = "{} - {}".format(command.get_name(), bot.l10n().translate(
                    event.peer_id, event.user_id, command.get_help()))
                page_data.append(text)
            self.reply_translated(event, bot, "help.page",
                                  None, page, "\n".join(page_data))
