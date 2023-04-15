class APIException(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(str(status_code))
