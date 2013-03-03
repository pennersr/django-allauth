try:
    from django.conf.urls import patterns, url
except ImportError:
    # for Django version less then 1.4
    from django.conf.urls.defaults import patterns, url
from django.utils import importlib

from allauth.socialaccount import providers

import app_settings

urlpatterns = patterns('', url('^', include('allauth.account.urls')))

if app_settings.SOCIALACCOUNT_ENABLED:
    urlpatterns += patterns('', url('^social/', 
                                    include('allauth.socialaccount.urls')))

for provider in providers.registry.get_list():
    try:
        prov_mod = importlib.import_module(provider.package + '.urls')
    except ImportError:
        continue
    prov_urlpatterns = getattr(prov_mod, 'urlpatterns', None)
    if prov_urlpatterns:
        urlpatterns += prov_urlpatterns
