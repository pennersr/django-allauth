from django.urls import path

from . import views


urlpatterns = [
    path('openid/login/', views.login, name="openid_login"),
    path('openid/callback/', views.callback, name='openid_callback'),
]
