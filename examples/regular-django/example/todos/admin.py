from django.contrib import admin

from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "text", "is_done", "created_at")
    list_filter = ("is_done",)
    search_fields = ("text",)
