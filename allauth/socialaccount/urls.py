from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^login/cancelled/$', views.login_cancelled,
        name='socialaccount_login_cancelled'),
    url(r'^login/error/$', views.login_error,
        name='socialaccount_login_error'),
    url(r'^signup/$', views.signup, name='socialaccount_signup'),
    url(r'^connections/$', views.connections, name='socialaccount_connections')
]
