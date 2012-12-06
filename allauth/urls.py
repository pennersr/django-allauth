from django.conf.urls.defaults import url, patterns, include
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
    except ImportError as e:
        if not "urls" in e:
            raise
        continue
    prov_urlpatterns = getattr(prov_mod, 'urlpatterns', None)
    if prov_urlpatterns:
        urlpatterns += prov_urlpatterns
