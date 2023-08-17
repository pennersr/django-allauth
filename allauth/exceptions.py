class ImmediateHttpResponse(Exception):
    """
    This exception is used to interrupt the flow of processing to immediately
    return a custom HttpResponse.
    """

    def __init__(self, response, stash_state=False):
        self.response = response
        self.stash_state = stash_state
