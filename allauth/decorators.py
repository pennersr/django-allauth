from functools import wraps

from allauth.core import ratelimit


def rate_limit(*, action, **rl_kwargs):
    def decorator(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            resp = ratelimit.consume_or_429(request, action=action, **rl_kwargs)
            if not resp:
                resp = function(request, *args, **kwargs)
            return resp

        return wrap

    return decorator
