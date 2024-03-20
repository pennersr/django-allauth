from django.urls import include, path, re_path

from allauth import app_settings as allauth_settings


_patterns = [
    path("", include("allauth.headless.base.urls")),
    path("", include("allauth.headless.account.urls")),
]

if allauth_settings.SOCIALACCOUNT_ENABLED:
    _patterns.append(path("", include("allauth.headless.socialaccount.urls")))

if allauth_settings.MFA_ENABLED:
    _patterns.append(path("", include("allauth.headless.mfa.urls")))

if allauth_settings.USERSESSIONS_ENABLED:
    _patterns.append(path("", include("allauth.headless.usersessions.urls")))

_version_patterns = [path("v1/", include(_patterns))]

urlpatterns = [
    re_path(
        r"(?P<client>browser|device)/",
        include(_version_patterns),
    )
]
