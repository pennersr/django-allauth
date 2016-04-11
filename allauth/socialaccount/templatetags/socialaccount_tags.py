import warnings

warnings.warn("{% load socialaccount_tags %} is deprecated, use"
              " {% load socialaccount %}", DeprecationWarning)

from .socialaccount import *  # noqa
