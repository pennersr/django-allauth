from django.conf.urls import url

from . import views

urlpatterns = [
    url('^draugiem/login/$', views.login, name="draugiem_login"),
    url('^draugiem/callback/$', views.callback, name='draugiem_callback'),
]
