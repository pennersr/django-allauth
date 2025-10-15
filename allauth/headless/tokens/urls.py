from django.urls import path

from allauth.headless.tokens import views


def build_urlpatterns(client):
    return [
        path(
            "tokens/refresh",
            views.RefreshTokenView.as_api_view(client=client),
            name="refresh",
        ),
    ]
