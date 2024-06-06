# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.lemonldap_provider.provider import (
    LemonLDAPProvider,
)
from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns


urlpatterns = default_urlpatterns(LemonLDAPProvider)
