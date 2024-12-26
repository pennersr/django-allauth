from django.urls import include, path

from allauth import app_settings as allauth_settings
from allauth.headless import app_settings
from allauth.headless.account import urls as account_urls
from allauth.headless.base import urls as base_urls
from allauth.headless.constants import Client


def build_urlpatterns(client):
    patterns = []
    patterns.extend(base_urls.build_urlpatterns(client))
    patterns.append(
        path(
            "",
            include(
                (account_urls.build_urlpatterns(client), "headless"),
                namespace="account",
            ),
        )
    )
    if allauth_settings.SOCIALACCOUNT_ENABLED:
        from allauth.headless.socialaccount import urls as socialaccount_urls

        patterns.append(
            path(
                "",
                include(
                    (socialaccount_urls.build_urlpatterns(client), "headless"),
                    namespace="socialaccount",
                ),
            )
        )

    if allauth_settings.MFA_ENABLED:
        from allauth.headless.mfa import urls as mfa_urls

        patterns.append(
            path(
                "",
                include(
                    (mfa_urls.build_urlpatterns(client), "headless"),
                    namespace="mfa",
                ),
            )
        )

    if allauth_settings.USERSESSIONS_ENABLED:
        from allauth.headless.usersessions import urls as usersessions_urls

        patterns.append(
            path(
                "",
                include(
                    (usersessions_urls.build_urlpatterns(client), "headless"),
                    namespace="usersessions",
                ),
            )
        )

    return [path("v1/", include(patterns))]


app_name = "headless"
urlpatterns = []
if Client.BROWSER in app_settings.CLIENTS:
    urlpatterns.append(
        path(
            "browser/",
            include(
                (build_urlpatterns(Client.BROWSER), "headless"),
                namespace="browser",
            ),
        )
    )
if Client.APP in app_settings.CLIENTS:
    urlpatterns.append(
        path(
            "app/",
            include((build_urlpatterns(Client.APP), "headless"), namespace="app"),
        )
    )

if app_settings.SERVE_SPECIFICATION:
    urlpatterns.append(
        path(
            "",
            include(
                "allauth.headless.spec.urls",
            ),
        )
    )
