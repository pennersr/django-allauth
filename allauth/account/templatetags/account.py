from __future__ import annotations

from django import template
from django.contrib.auth.base_user import AbstractBaseUser

from allauth.account.utils import user_display


register = template.Library()


@register.simple_tag(name="user_display")
def user_display_tag(user: AbstractBaseUser) -> str:
    """
    Example usage::

        {% user_display user %}

    or if you need to use in a {% blocktrans %}::

        {% user_display user as user_display %}
        {% blocktrans %}
        {{ user_display }} has sent you a gift.
        {% endblocktrans %}

    """
    return user_display(user)
