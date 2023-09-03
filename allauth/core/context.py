from contextlib import contextmanager
from contextvars import ContextVar


_request_var = ContextVar("request", default=None)


def __getattr__(name):
    if name == "request":
        return _request_var.get()
    raise AttributeError(name)


@contextmanager
def request_context(request):
    token = _request_var.set(request)
    try:
        yield
    finally:
        _request_var.reset(token)
