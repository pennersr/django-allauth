import warnings

from allauth.headless.tokens.strategies.base import AbstractTokenStrategy


__all__ = ["AbstractTokenStrategy"]

warnings.warn(
    "allauth.headless.tokens.base.AbstractTokenStrategy is deprecated, use allauth.headless.tokens.strategies.base.AbstractTokenStrategy"
)
