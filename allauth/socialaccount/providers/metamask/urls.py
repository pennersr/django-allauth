from django.urls import path
from .views import login_api


urlpatterns = [path("metamask/login/", views.login_url, name="metamask_login")]
