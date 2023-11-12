import warnings

from allauth.core.ratelimit import clear, consume, consume_or_429


__all__ = ["consume", "consume_or_429", "clear"]
warnings.warn("allauth.ratelimit is deprecated, use allauth.core.ratelimit")
