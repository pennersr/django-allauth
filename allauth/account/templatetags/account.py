from django import template

from allauth.account.utils import user_display


register = template.Library()


@register.simple_tag(name="user_display")
def user_display_tag(user):
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
