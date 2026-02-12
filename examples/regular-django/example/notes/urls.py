from django.urls import path

from .views import note_delete, note_list


urlpatterns = [
    path("", note_list, name="notes_list"),
    path("<int:pk>/delete/", note_delete, name="notes_delete"),
]
