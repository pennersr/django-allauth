from django.conf.urls.defaults import *
from django.utils import importlib

from allauth.socialaccount.providers import get_providers

import app_settings

urlpatterns = patterns('',
                       url('^', include('allauth.account.urls')))
                       
if app_settings.SOCIALACCOUNT_ENABLED:
    urlpatterns += patterns('',
                            url('^social/', include('allauth.socialaccount.urls')))


for provider in get_providers():
    try:
        prov_mod = importlib.import_module(provider.package + '.urlpatterns')
    except ImportError:
        continue
    prov_urlpatterns = getattr(prov_mod, 'urlpatterns', None)
    if prov_urlpatterns:
        urlpatterns += prov_urlpatterns


if app_settings.FACEBOOK_ENABLED:
    urlpatterns += patterns('',
                            url('^facebook/', include('allauth.facebook.urls')))
if app_settings.OPENID_ENABLED:
    urlpatterns += patterns('',
                            url('^openid/', include('allauth.openid.urls')))



