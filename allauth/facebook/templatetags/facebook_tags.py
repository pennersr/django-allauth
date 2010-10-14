from django import template
from django.conf import settings

from allauth.facebook.models import FacebookApp
from allauth.socialaccount.app_settings import QUERY_EMAIL

register = template.Library()

@register.inclusion_tag('facebook/fbconnect.html', takes_context=True)
def fbconnect(context):
    perm_list = []
    if QUERY_EMAIL:
        perm_list.append('email')
    perms = ','.join(perm_list)
    return {'facebook_app': FacebookApp.objects.get_current(),
            'facebook_perms': perms}

