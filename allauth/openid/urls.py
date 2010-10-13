from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
                       url('^login/$', views.login, name="openid_login"),
                       url('^callback/$', views.callback),
                       )
