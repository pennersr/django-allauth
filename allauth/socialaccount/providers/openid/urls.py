from django.conf.urls import url

from . import views

urlpatterns = [
    url('^openid/login/$', views.login, name="openid_login"),
    url('^openid/callback/$', views.callback, name='openid_callback'),
]
