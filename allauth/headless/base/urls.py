from django.urls import path

from allauth.headless.base import views


def build_urlpatterns(client):
    return [
        path(
            "config",
            views.ConfigView.as_api_view(client=client),
            name="config",
        ),
    ]
