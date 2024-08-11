from importlib import import_module
from typing import List, Union

from django.urls import URLPattern, URLResolver, include, path
from django.views.generic.base import RedirectView

from allauth.socialaccount import providers

from . import app_settings


def build_provider_urlpatterns() -> List[Union[URLPattern, URLResolver]]:
    # Provider urlpatterns, as separate attribute (for reusability).
    provider_urlpatterns: List[Union[URLPattern, URLResolver]] = []
    provider_classes = providers.registry.get_class_list()

    # We need to move the OpenID Connect provider to the end. The reason is that
    # matches URLs that the builtin providers also match.
    #
    # NOTE: Only needed if OPENID_CONNECT_URL_PREFIX is blank.
    provider_classes = [
        cls for cls in provider_classes if cls.id != "openid_connect"
    ] + [cls for cls in provider_classes if cls.id == "openid_connect"]
    for provider_class in provider_classes:
        prov_mod = import_module(provider_class.get_package() + ".urls")
        prov_urlpatterns = getattr(prov_mod, "urlpatterns", None)
        if prov_urlpatterns:
            provider_urlpatterns += prov_urlpatterns
    return provider_urlpatterns


urlpatterns: List[Union[URLPattern, URLResolver]] = []
if not app_settings.HEADLESS_ONLY:
    urlpatterns += [path("", include("allauth.account.urls"))]
    if app_settings.MFA_ENABLED:
        urlpatterns += [path("2fa/", include("allauth.mfa.urls"))]

if app_settings.SOCIALACCOUNT_ENABLED and not app_settings.HEADLESS_ONLY:
    urlpatterns += [path("3rdparty/", include("allauth.socialaccount.urls"))]

    # DEPRECATED! -- deal with legacy URLs
    urlpatterns += [
        path(
            "social/login/cancelled/",
            RedirectView.as_view(
                pattern_name="socialaccount_login_cancelled", permanent=True
            ),
        ),
        path(
            "social/login/error/",
            RedirectView.as_view(
                pattern_name="socialaccount_login_error", permanent=True
            ),
        ),
        path(
            "social/signup/",
            RedirectView.as_view(pattern_name="socialaccount_signup", permanent=True),
        ),
        path(
            "social/connections/",
            RedirectView.as_view(
                pattern_name="socialaccount_connections", permanent=True
            ),
        ),
    ]
    # (end DEPRECATED)

if app_settings.SOCIALACCOUNT_ENABLED:
    urlpatterns += build_provider_urlpatterns()

if app_settings.USERSESSIONS_ENABLED and not app_settings.HEADLESS_ONLY:
    urlpatterns += [path("sessions/", include("allauth.usersessions.urls"))]
