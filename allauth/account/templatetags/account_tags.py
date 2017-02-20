import warnings

from .account import *  # noqa


warnings.warn("{% load account_tags %} is deprecated, use {% load account %}",
              DeprecationWarning)
