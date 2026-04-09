from __future__ import annotations

from django.urls import URLPattern, URLResolver, include, path

from allauth.headless.constants import Client
from allauth.headless.usersessions import views


def build_urlpatterns(client: Client) -> list[URLPattern | URLResolver]:
    return [
        path(
            "auth/",
            include(
                [
                    path(
                        "sessions",
                        views.SessionsView.as_api_view(client=client),
                        name="sessions",
                    ),
                ]
            ),
        )
    ]
