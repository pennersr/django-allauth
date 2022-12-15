# -*- coding: utf-8 -*-
import itertools

from django.urls import include, path

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.socialaccount.providers.openid_connect.provider import (
    provider_classes,
)
from allauth.socialaccount.providers.openid_connect.views import (
    OpenIDConnectAdapter,
)


def _factory(_provider_id):
    class OpenIDConnectAdapterServer(OpenIDConnectAdapter):
        provider_id = _provider_id

    return OpenIDConnectAdapterServer


def default_urlpatterns(provider):
    adapter_class = _factory(provider.id)
    urlpatterns = [
        path(
            "login/",
            OAuth2LoginView.adapter_view(adapter_class),
            name=provider.id + "_login",
        ),
        path(
            "login/callback/",
            OAuth2CallbackView.adapter_view(adapter_class),
            name=provider.id + "_callback",
        ),
    ]

    return [path(provider.get_slug() + "/", include(urlpatterns))]


urlpatterns = itertools.chain.from_iterable(
    [default_urlpatterns(provider_class) for provider_class in provider_classes]
)
