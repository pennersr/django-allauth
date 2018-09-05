from django.conf.urls import url

from . import views


urlpatterns = [
    url('^telegram/login/$', views.telegram_login, name="telegram_login")
]
