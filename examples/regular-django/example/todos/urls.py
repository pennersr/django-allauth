from django.urls import path

from .views import todo_delete, todo_list, todo_toggle


urlpatterns = [
    path("", todo_list, name="todos_list"),
    path("<int:pk>/toggle/", todo_toggle, name="todos_toggle"),
    path("<int:pk>/delete/", todo_delete, name="todos_delete"),
]
