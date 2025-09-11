from django.contrib import admin, messages
from django.utils.html import escape
from django.utils.safestring import mark_safe

from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.models import Client, Token


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    raw_id_fields = ("owner",)
    list_display = (
        "name",
        "id",
        "type",
        "owner",
        "skip_consent",
        "allow_uri_wildcards",
        "created_at",
    )
    readonly_fields = ("secret", "created_at")
    list_filter = ("type", "skip_consent", "allow_uri_wildcards")

    def save_model(self, request, obj, form, change):
        if not change:
            adapter = get_adapter()
            secret = adapter.generate_client_secret()
            obj.set_secret(secret)
            self.message_user(
                request,
                mark_safe(
                    f'The client secret is only shown once: <input readonly size="{len(secret)}" type="text" value="{escape(secret)}">'
                ),  # nosec
                level=messages.WARNING,
            )
        return super().save_model(request, obj, form, change)


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    raw_id_fields = ("client", "user")
    list_display = (
        "client",
        "type",
        "user",
        "created_at",
        "expires_at",
    )
    list_filter = ("type",)
