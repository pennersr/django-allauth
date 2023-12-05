from django.urls import path

from allauth.usersessions import views


urlpatterns = [
    path("", views.list_usersessions, name="usersessions_list"),
]
