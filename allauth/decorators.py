from functools import wraps

from django.shortcuts import render

from allauth import ratelimit


def rate_limit(*, action, **rl_kwargs):
    from allauth.account import app_settings

    rate = app_settings.RATE_LIMITS.get(action)
    if rate:
        rate = ratelimit.parse(rate)
        rl_kwargs.setdefault("duration", rate.duration)
        rl_kwargs.setdefault("amount", rate.amount)

    def decorator(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            if ratelimit.consume(request, action=action, **rl_kwargs):
                return function(request, *args, **kwargs)
            else:
                return render(
                    request, "429." + app_settings.TEMPLATE_EXTENSION, status=429
                )

        return wrap

    return decorator
