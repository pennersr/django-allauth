# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.netiq.provider import NetIQProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(NetIQProvider)
