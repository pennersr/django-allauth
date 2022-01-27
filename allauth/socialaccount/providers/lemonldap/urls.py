# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.lemonldap.provider import LemonldapProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(LemonldapProvider)
