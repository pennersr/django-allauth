try:
    from django.conf.urls import patterns, url
except ImportError:
    # for Django version less then 1.4
    from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
                       url('^openid/login/$', views.login, name="openid_login"),
                       url('^openid/callback/$', views.callback),
                       )
