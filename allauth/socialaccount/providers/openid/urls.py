from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
                       url('^openid/login/$', views.login,
                           name="openid_login"),
                       url('^openid/callback/$', views.callback,
                           name='openid_callback'),
                       )
