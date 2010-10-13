from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
                       url('^login/$', views.login, name="twitter_login"),
                       url('^callback/$', views.callback),
                       url('^login/done/$', views.login_done),
                       )
