from typing import List, Union

from django.urls import URLPattern, URLResolver, path

from allauth.mfa.recovery_codes import views


urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path("", views.view_recovery_codes, name="mfa_view_recovery_codes"),
    path(
        "generate/",
        views.generate_recovery_codes,
        name="mfa_generate_recovery_codes",
    ),
    path(
        "download/",
        views.download_recovery_codes,
        name="mfa_download_recovery_codes",
    ),
]
