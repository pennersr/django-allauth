from allauth.core.internal import ratelimit


def rate_limit(**kwargs):
    return ratelimit.decorator(app="allauth.account", **kwargs)
