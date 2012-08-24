import warnings

warnings.warn("{% load account_tags %} is deprecated, use {% load account %}",
              DeprecationWarning)

from account import *
