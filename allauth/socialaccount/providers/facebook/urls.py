from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
                       url('^facebook/login/$', views.login, name="facebook_login"),
                       url('^facebook/channel/$', views.channel, name='facebook_channel'),
                       )
