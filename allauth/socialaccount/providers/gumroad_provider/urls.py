# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.gumroad_provider.provider import GumroadProvider
from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns


urlpatterns = default_urlpatterns(GumroadProvider)
