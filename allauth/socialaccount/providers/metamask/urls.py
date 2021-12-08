from django.urls import path

from . import views


urlpatterns = [path("metamask/login/", views.metamask_login, name="metamask_login")]
