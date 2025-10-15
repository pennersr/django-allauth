import warnings

from allauth.headless.tokens.strategies.sessions import SessionTokenStrategy


__all__ = ["SessionTokenStrategy"]

warnings.warn(
    "allauth.headless.tokens.sessions.SessionTokenStrategy is deprecated, use allauth.headless.tokens.strategies.sessions.SessionTokenStrategy"
)
