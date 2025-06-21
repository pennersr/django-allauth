from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress, EmailConfirmation


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ("email", "user", "primary", "verified")
    list_filter = ("primary", "verified")
    search_fields = []
    raw_id_fields = ("user",)
    actions = ["make_verified"]

    def get_search_fields(self, request):
        base_fields = get_adapter().get_user_search_fields()
        return ["email"] + list(map(lambda a: "user__" + a, base_fields))

    def make_verified(self, request, queryset):
        for email_address in queryset.filter(verified=False).iterator():
            if email_address.set_verified():
                signals.email_confirmed.send(
                    sender=EmailAddress,
                    request=request,
                    email_address=email_address,
                )
                self.message_user(
                    request,
                    _("Marked {email} as verified.").format(email=email_address.email),
                    level=messages.SUCCESS,
                )
            else:
                self.message_user(
                    request,
                    _("Failed to mark {email} as verified.").format(
                        email=email_address.email
                    ),
                    level=messages.ERROR,
                )

    make_verified.short_description = _("Mark selected email addresses as verified")  # type: ignore[attr-defined]


class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ("email_address", "created", "sent", "key")
    list_filter = ("sent",)
    raw_id_fields = ("email_address",)


if not app_settings.EMAIL_CONFIRMATION_HMAC:
    admin.site.register(EmailConfirmation, EmailConfirmationAdmin)
admin.site.register(EmailAddress, EmailAddressAdmin)
