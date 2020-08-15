

class Error(Exception):
    pass


class FileTypeError(Error):
    pass


class ApiError(Error, RuntimeError):
    pass


class HttpFailed(ApiError):

    def __init__(self, status: int):
        self._status = status

    def __repr__(self):
        return f'<HttpFailed, status_code={self._status}>'

    def __str__(self):
        return self.__repr__()


class NetworkError(Error, IOError):
    pass


class ResponseError(NetworkError):
    pass


class OperationError(Error, RuntimeError):
    pass
