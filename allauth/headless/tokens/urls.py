from __future__ import annotations

from django.urls import URLPattern, path

from allauth.headless.constants import Client
from allauth.headless.tokens import views


def build_urlpatterns(client: Client) -> list[URLPattern]:
    return [
        path(
            "tokens/refresh",
            views.RefreshTokenView.as_api_view(client=client),
            name="refresh",
        ),
    ]
