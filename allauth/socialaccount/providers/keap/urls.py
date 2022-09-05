# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.keap.provider import KeapProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

urlpatterns = default_urlpatterns(KeapProvider)
