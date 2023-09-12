import warnings

from allauth.core.exceptions import ImmediateHttpResponse


__all__ = ["ImmediateHttpResponse"]


warnings.warn("allauth.exceptions is deprecated, use allauth.core.exceptions")
