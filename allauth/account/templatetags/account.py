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
        {% blocktrans %}{{ user_display }} has sent you a gift.{% endblocktrans %}
    
    """
    bits = token.split_contents()
    if len(bits) == 2:
        user = bits[1]
        as_var = None
    elif len(bits) == 4:
        user = bits[1]
        as_var = bits[3]
    else:
        raise template.TemplateSyntaxError("'%s' takes either two or four arguments" % bits[0])
    
    return UserDisplayNode(user, as_var)


class HasProviderNode(template.Node):

    def __init__(self, user, provider, as_var=None):
        self.user_var = template.Variable(user)
        self.provider = provider
        self.as_var = as_var

    def render(self, context):
        user = self.user_var.resolve(context)

        try:
          display = user.socialaccount_set.filter(provider=self.provider).exists()
        except AttributeError:
          display = False

        if self.as_var:
            context[self.as_var] = display
            return ""
        return display

@register.tag(name="has_provider")
def has_provider(parser, token):
    """
    Example usage:

        {% has_provider user "facebook" %}

        {% has_provider user "facebook" as has_fb %}

    """
    bits = token.split_contents()
    if len(bits) == 3:
        tag_name = bits[0]
        user = bits[1]
        provider = bits[2]
        as_var = None
    elif len(bits) == 5:
        tag_name = bits[0]
        user = bits[1]
        provider = bits[2]
        as_var = bits[4]
    else:
        raise template.TemplateSyntaxError("'%s' takes either three or five arguments" % tag_name)
    if not (provider[0] == provider[-1] and provider[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)

    return HasProviderNode(user, provider[1:-1], as_var)

