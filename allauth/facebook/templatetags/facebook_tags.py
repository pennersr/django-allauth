from django import template
from django.conf import settings

from allauth.facebook.models import FacebookApp

register = template.Library()

@register.inclusion_tag('facebook/fbconnect.html', takes_context=True)
def fbconnect(context):
    return {'facebook_app': FacebookApp.objects.get_current() }

