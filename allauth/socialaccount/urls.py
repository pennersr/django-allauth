from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
    url('^login/cancelled/$', views.login_cancelled, 
        name='socialaccount_login_cancelled'),
    url('^login/error/$', views.login_error, name='socialaccount_login_error'),
    url('^signup/$', views.signup, name='socialaccount_signup'),
    url('^connections/$', views.connections, name='socialaccount_connections'))
