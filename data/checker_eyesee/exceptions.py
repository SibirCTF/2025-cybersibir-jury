class BaseCheckerException(Exception):
    ...


class FlagNotFoundException(BaseCheckerException):
    ...


class DataIsCorrupt(BaseCheckerException):
    ...
