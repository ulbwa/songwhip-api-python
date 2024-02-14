class APIException(Exception):
    """
    An exception raised when an error occurs during API operations.

    :ivar status_code: The HTTP status code associated with the exception.
    :ivar message: A message describing the exception.
    """

    def __init__(self, status_code: int, message: str | None = None):
        """
        Initializes an APIException instance.

        :param status_code: The HTTP status code associated with the exception.
        :param message: A message describing the exception.
        """
        self.status_code = status_code
        self.message = message

        super().__init__(
            str(status_code)
            if message is None
            else "{}: {}".format(status_code, message)
        )


__all__ = ("APIException",)
