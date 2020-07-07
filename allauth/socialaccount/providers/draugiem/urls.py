from django.urls import path

from . import views


urlpatterns = [
    path('draugiem/login/', views.login, name="draugiem_login"),
    path('draugiem/callback/', views.callback, name='draugiem_callback'),
]
