from __future__ import annotations

from django.core.exceptions import ValidationError
from django.http import HttpRequest

from allauth.core import context


class BaseAdapter:
    error_messages: dict

    def __init__(self, request: HttpRequest | None = None) -> None:
        # Explicitly passing `request` is deprecated, just use:
        # `allauth.core.context.request`.
        self.request = context.request

    def validation_error(self, code, *args) -> ValidationError:
        message = self.error_messages[code]
        if args:
            message = message % args
        exc = ValidationError(message, code=code)
        return exc
