from django import template
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.template.defaulttags import token_kwargs

from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.facebook.models import FacebookProvider

register = template.Library()

def fbconnect(context):
    perm_list = []
    if QUERY_EMAIL:
        perm_list.append('email')
    perms = ','.join(perm_list)
    request = context['request']
    try:
        app = SocialApp.objects.get_current(FacebookProvider.id)
    except SocialApp.DoesNotExist:
        raise ImproperlyConfigured("No Facebook app configured: please"
                                   " add a SocialApp using the Django admin")
    return {'facebook_app': app,
            'facebook_channel_url': 
            request.build_absolute_uri(reverse('facebook_channel')),
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

