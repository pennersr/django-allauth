class ImmediateHttpResponse(Exception):
    """
    This exception is used to interrupt the flow of processing to immediately
    return a custom HttpResponse.
    """

    def __init__(self, response):
        self.response = response


class ReauthenticationRequired(Exception):
    """
    The action could not be performed because the user needs to
    reauthenticate.
    """

    pass


class SignupClosedException(Exception):
    """
    Throws when attemtping to signup while signup is closed.
    """

    pass
