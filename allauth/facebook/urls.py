from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
                       url('^login/$', views.login, name="facebook_login"),
                       url('^channel/$', views.channel, name='facebook_channel'),
                       )
