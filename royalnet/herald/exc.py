class Closed(BaseException):
    """
    The websocket should be closed.
    """

    def __init__(self, code: int, reason: str):
        self.code: int = code
        self.reason: str = reason

    def __repr__(self):
        code = self.code
        reason = self.reason
        return f"{self.__class__.__qualname__}({code=}, {reason=})"
