from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaulttags import token_kwargs

from allauth.facebook.models import FacebookApp
from allauth.socialaccount.app_settings import QUERY_EMAIL

register = template.Library()

def fbconnect(context):
    perm_list = []
    if QUERY_EMAIL:
        perm_list.append('email')
    perms = ','.join(perm_list)
    request = context['request']
    return {'facebook_app': FacebookApp.objects.get_current(),
            'facebook_channel_url': request.build_absolute_uri(reverse('facebook_channel')),
            'facebook_perms': perms}

class FacebookLoginURLNode(template.Node):
    def __init__(self, params):
        self.params = params

    def render(self, context):
        query = dict([(name, var.resolve(context)) for name, var
                      in self.params.iteritems()])
        next = query.get('next', '')
        if not next:
            request = context['request']
            next = request.REQUEST.get('next', '')
        if next:
            next = "'%s'" % next
        return "javascript:FB_login(%s)" % next

def facebook_login_url(parser, token):
    bits = token.split_contents()
    params = token_kwargs(bits[1:], parser, support_legacy=False)
    return FacebookLoginURLNode(params)
    

def register_tags(reg):
    reg.inclusion_tag('facebook/fbconnect.html', takes_context=True)(fbconnect)
    reg.tag()(facebook_login_url)

register_tags(register)

