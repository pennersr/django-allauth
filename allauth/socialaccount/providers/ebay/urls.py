# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.ebay.provider import EBayProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(EBayProvider)
