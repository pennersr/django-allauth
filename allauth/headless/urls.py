from django.urls import include, path, re_path

from allauth import app_settings as allauth_settings
from allauth.headless.account import urls as account_urls
from allauth.headless.base import urls as base_urls


def build_urlpatterns(client):
    patterns = []
    patterns.extend(base_urls.build_urlpatterns(client))
    patterns.extend(account_urls.build_urlpatterns(client))
    if allauth_settings.SOCIALACCOUNT_ENABLED:
        from allauth.headless.socialaccount import urls as socialaccount_urls

        patterns.extend(socialaccount_urls.build_urlpatterns(client))

    if allauth_settings.MFA_ENABLED:
        from allauth.headless.mfa import urls as mfa_urls

        patterns.extend(mfa_urls.build_urlpatterns(client))

    if allauth_settings.USERSESSIONS_ENABLED:
        from allauth.headless.usersessions import urls as usersessions_urls

        patterns.extend(usersessions_urls.build_urlpatterns(client))

    return [path("v1/", include(patterns))]


urlpatterns = [
    path("browser/", include(build_urlpatterns("browser"))),
    path("api/", include(build_urlpatterns("api"))),
]
