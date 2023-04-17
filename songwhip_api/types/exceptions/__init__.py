from typing import Optional


class APIException(Exception):
    def __init__(self, status_code: int, message: Optional[str] = None):
        self.status_code = status_code
        self.message = message
        super().__init__(
            str(status_code)
            if message is None
            else "{}: {}".format(status_code, message)
        )
