from django.conf.urls.defaults import *

import views

urlpatterns = \
    patterns('',
             url('^login/$', views.login, name='socialaccount_login'),
             url('^signup/$', views.signup, name='socialaccount_setup'),
             url('^connections/$', views.connections, name='socialaccount_connections'))
