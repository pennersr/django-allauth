from typing import List, Union

from django.urls import URLPattern, URLResolver, path

from allauth.mfa import app_settings
from allauth.mfa.base import views


urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path("", views.index, name="mfa_index"),
    path("authenticate/", views.authenticate, name="mfa_authenticate"),
    path("reauthenticate/", views.reauthenticate, name="mfa_reauthenticate"),
]

if app_settings._TRUST_STAGE_ENABLED:
    urlpatterns.append(path("trust/", views.trust, name="mfa_trust"))
