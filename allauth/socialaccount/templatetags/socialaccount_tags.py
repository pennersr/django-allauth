import warnings

from .socialaccount import *  # noqa


warnings.warn("{% load socialaccount_tags %} is deprecated, use"
              " {% load socialaccount %}", DeprecationWarning)
