from django.urls import path
from .views import login_api

urlpatterns = [
    path("metamask/login/", login_api, name="metamask_login"),
]
