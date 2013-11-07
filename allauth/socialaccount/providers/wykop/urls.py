from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
   url('^wykop/login/token/$', views.login_by_token,
       name="wykop_login_by_token"),
)
