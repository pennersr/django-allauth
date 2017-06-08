from django import template

from allauth.account.utils import user_display


register = template.Library()


class UserDisplayNode(template.Node):

    def __init__(self, user, as_var=None):
        self.user_var = template.Variable(user)
        self.as_var = as_var

    def render(self, context):
        user = self.user_var.resolve(context)

        display = user_display(user)

        if self.as_var:
            context[self.as_var] = display
            return ""
        return display


@register.tag(name="user_display")
def do_user_display(parser, token):
    """
    Example usage::

        {% user_display user %}

    or if you need to use in a {% blocktrans %}::

        {% user_display user as user_display %}
        {% blocktrans %}
        {{ user_display }} has sent you a gift.
        {% endblocktrans %}

    """
    bits = token.split_contents()
    if len(bits) == 2:
        user = bits[1]
        as_var = None
    elif len(bits) == 4:
        user = bits[1]
        as_var = bits[3]
    else:
        raise template.TemplateSyntaxError(
            "'%s' takes either two or four arguments" % bits[0])

    return UserDisplayNode(user, as_var)

class SocialAccountsNode(template.Node):

    def __init__(self, user, as_var=None):
        self.user_var = template.Variable(user)
        self.as_var = as_var

    def render(self, context):
        user = self.user_var.resolve(context)

        try:
          display = { provider : user.socialaccount_set.filter(provider=provider) for provider in user.socialaccount_set.values_list('provider', flat=True) }
        except AttributeError, e:
          display = False

        if self.as_var:
            context[self.as_var] = display
            return ""
        return display

@register.tag(name="get_social_accounts")
def get_social_accounts(parser, token):
    """
    Example usage:

        {% get_social_accounts user %}

        {% get_social_accounts user as accounts %}

    """
    bits = token.split_contents()
    if len(bits) == 2:
        tag_name = bits[0]
        user = bits[1]
        as_var = None
    elif len(bits) == 4:
        tag_name = bits[0]
        user = bits[1]
        as_var = bits[3]
    else:
        raise template.TemplateSyntaxError("'%s' takes either two or four arguments" % tag_name)

    return SocialAccountsNode(user, as_var)
