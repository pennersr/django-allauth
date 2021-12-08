from django.urls import path
from .views import login_api


urlpatterns = [path("metamask/login_url/", views.login_url, name="metamask_login")]
