from django.contrib import admin

from allauth.usersessions.models import UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    list_display = ("user", "created_at", "last_seen_at", "ip", "user_agent")
    search_fields = [
        "user__pk",
        "user__username",
        "ip",
    ]
