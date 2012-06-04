from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
                       url('^openid/login/$', views.login, name="openid_login"),
                       url('^openid/callback/$', views.callback),
                       )
