from django.urls import path

from .views import nonce, verify


urlpatterns = [
    path("metamask/nonce/", nonce, name="metamask_nonce"),
    path("metamask/verify/", verify, name="metamask_verify"),
]
