from django.conf.urls import patterns, url

from . import views
from ..utils import signup_view

urlpatterns = patterns('',
    url('^login/cancelled/$', views.login_cancelled,
        name='socialaccount_login_cancelled'),
    url('^login/error/$', views.login_error, name='login_error'),
    url('^signup/$', signup_view().as_view(), name='signup'),
    url('^connections/$', views.connections, name='connections'))
