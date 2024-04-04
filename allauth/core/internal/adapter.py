from django.core.exceptions import ValidationError

from allauth.core import context


class BaseAdapter:
    def __init__(self, request=None):
        # Explicitly passing `request` is deprecated, just use:
        # `allauth.core.context.request`.
        self.request = context.request

    def validation_error(self, code, *args):
        message = self.error_messages[code]
        if args:
            message = message % args
        exc = ValidationError(message, code=code)
        return exc
