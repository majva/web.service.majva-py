
class AuthenticateSto:
    success: bool
    message: str
    statusno: int
    data: object

    def __init__(self, success: bool, message: str, statusno: int, data: object):
        self.success = success
        self.message = message
        self.statusno = statusno
        self.data = data
