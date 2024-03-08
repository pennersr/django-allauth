from importlib import import_module

from django.urls import include, path

from allauth.socialaccount import providers

from . import app_settings


urlpatterns = [path("", include("allauth.account.urls"))]
if app_settings.MFA_ENABLED:
    urlpatterns += [path("2fa/", include("allauth.mfa.urls"))]

if app_settings.SOCIALACCOUNT_ENABLED:
    urlpatterns += [path("social/", include("allauth.socialaccount.urls"))]

if app_settings.USERSESSIONS_ENABLED:
    urlpatterns += [path("sessions/", include("allauth.usersessions.urls"))]

# Provider urlpatterns, as separate attribute (for reusability).
provider_urlpatterns = []
provider_classes = providers.registry.get_class_list()

# We need to move the OpenID Connect provider to the end. The reason is that
# matches URLs that the builtin providers also match.
#
# NOTE: Only needed if OPENID_CONNECT_URL_PREFIX is blank.
provider_classes = [cls for cls in provider_classes if cls.id != "openid_connect"] + [
    cls for cls in provider_classes if cls.id == "openid_connect"
]
for provider_class in provider_classes:
    prov_mod = import_module(provider_class.get_package() + ".urls")
    prov_urlpatterns = getattr(prov_mod, "urlpatterns", None)
    if prov_urlpatterns:
        provider_urlpatterns += prov_urlpatterns

urlpatterns += provider_urlpatterns
