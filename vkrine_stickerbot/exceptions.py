class VKRINEException(BaseException):
    pass


class CommandException(VKRINEException):
    def __init__(self, message, *args, **kwargs):
        super().__init__(message, args, kwargs)
        self.__message__ = message
        self.__args__ = args
        self.__kwargs__ = kwargs

    def get_message(self):
        return self.__message__

    def get_args(self):
        return self.__args__

    def get_kwargs(self):
        return self.__kwargs__


class NumberInvalidException(CommandException):
    def __init__(self, message, *args, **kwargs):
        if not message:
            message = "commands.generic.num.invalid"
        super().__init__(message, *args, **kwargs)


class UserNotFoundException(CommandException):
    def __init__(self, message, *args, **kwargs):
        if not message:
            message = "commands.generic.user.not_found"
        super().__init__(message, *args, **kwargs)


class CommandNotFoundException(CommandException):
    def __init__(self, message, *args, **kwargs):
        if not message:
            message = "commands.generic.not_found"
        super().__init__(message, *args, **kwargs)


class SyntaxError(CommandException):
    def __init__(self, message, *args, **kwargs):
        if not message:
            message = "commands.generic.syntax"
        super().__init__(message, *args, **kwargs)


class WrongUsageException(CommandException):
    pass
