from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url('^login/cancelled/$', views.login_cancelled,
        name='login_cancelled'),
    url('^login/error/$', views.login_error, name='login_error'),
    url('^signup/$', views.signup, name='signup'),
    url('^connections/$', views.connections, name='connections'))
