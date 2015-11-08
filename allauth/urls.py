from django.conf.urls import url, include
from django.conf import settings
from allauth.compat import importlib

from allauth.socialaccount import providers

from . import app_settings

urlpatterns = [url('^', include('allauth.account.urls'))]

if app_settings.SOCIALACCOUNT_ENABLED:
    urlpatterns += [url('^social/', include('allauth.socialaccount.urls'))]

# TODO: Providers register with the provider registry when loaded. Here, we
# build the URLs for all registered providers. So, we really need to be sure
# all providers did register, which is why we're forcefully importing the
# `provider` modules here. The overall mechanism is way to magical and depends
# on the import order et al, so all of this really needs to be revisited.
for app in settings.INSTALLED_APPS:
    if app.startswith('allauth.socialaccount.providers.'):
        try:
            importlib.import_module(app + '.provider')
        except ImportError:
            pass
# (end TODO)

for provider in providers.registry.get_list():
    try:
        prov_mod = importlib.import_module(provider.package + '.urls')
    except ImportError:
        continue
    prov_urlpatterns = getattr(prov_mod, 'urlpatterns', None)
    if prov_urlpatterns:
        urlpatterns += prov_urlpatterns
