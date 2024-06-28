from typing import List, Union

from django.urls import URLPattern, URLResolver, path

from allauth.mfa.totp import views


urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path("activate/", views.activate_totp, name="mfa_activate_totp"),
    path("deactivate/", views.deactivate_totp, name="mfa_deactivate_totp"),
]
