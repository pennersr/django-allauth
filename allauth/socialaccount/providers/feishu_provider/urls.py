# -*- coding: utf-8 -*-

from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import FeishuProvider


urlpatterns = default_urlpatterns(FeishuProvider)
