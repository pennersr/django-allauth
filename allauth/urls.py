from importlib import import_module

from django.conf.urls import include, url

from allauth.socialaccount import providers

from . import app_settings


urlpatterns = [url(r'^', include('allauth.account.urls'))]

if app_settings.SOCIALACCOUNT_ENABLED:
    urlpatterns += [url(r'^social/', include('allauth.socialaccount.urls'))]

# Provider urlpatterns, as separate attribute (for reusability).
provider_urlpatterns = []
for provider in providers.registry.get_list():
    try:
        prov_mod = import_module(provider.get_package() + '.urls')
    except ImportError:
        continue
    prov_urlpatterns = getattr(prov_mod, 'urlpatterns', None)
    if prov_urlpatterns:
        provider_urlpatterns += prov_urlpatterns
urlpatterns += provider_urlpatterns
