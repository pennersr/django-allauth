from __future__ import annotations

from django.urls import URLPattern, path

from allauth.headless.base import views
from allauth.headless.constants import Client


def build_urlpatterns(client: Client) -> list[URLPattern]:
    return [
        path(
            "config",
            views.ConfigView.as_api_view(client=client),
            name="config",
        ),
    ]
