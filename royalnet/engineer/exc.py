class EngineerException(Exception):
    pass


class ScrapException(EngineerException):
    pass


class DeliberateException(ScrapException):
    pass
