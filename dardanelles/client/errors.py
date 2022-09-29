class RemoteError(BaseException):
    """Can't reach pandarus-remote web service"""

    pass


class AlreadyExists(BaseException):
    """Resource has already been calculated"""

    pass
