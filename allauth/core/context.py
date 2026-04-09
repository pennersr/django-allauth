from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar

from django.http import HttpRequest


_request_var: ContextVar[HttpRequest | None] = ContextVar("request", default=None)


def __getattr__(name):
    if name == "request":
        return _request_var.get()
    raise AttributeError(name)


@contextmanager
def request_context(request: HttpRequest):
    token = _request_var.set(request)
    try:
        yield
    finally:
        _request_var.reset(token)
