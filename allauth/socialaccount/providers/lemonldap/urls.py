from allauth.socialaccount.providers.lemonldap.provider import (
    LemonLDAPProvider,
)
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(LemonLDAPProvider)
