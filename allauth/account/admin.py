from django.contrib import admin

from .models import EmailConfirmation, EmailAddress
from . import app_settings
from ..utils import get_user_model
from . import signals
from .adapter import get_adapter

User = get_user_model()


class EmailAddressAdmin(admin.ModelAdmin):
    actions = ['verify_email']
    list_display = ('email', 'user', 'primary', 'verified')
    list_filter = ('primary', 'verified')
    search_fields = ['email'] + list(map(lambda a: 'user__' + a,
                                    filter(lambda a: a and hasattr(User(), a),
                                           [app_settings.USER_MODEL_USERNAME_FIELD,
                                            'first_name',
                                            'last_name'])))
    raw_id_fields = ('user',)

    def verify_email(self, request, queryset):
        """
        A way to verify a user email if their email provider refuses to accept your email.
        """
        for email_address in queryset:
            get_adapter().confirm_email(request, email_address)
            signals.email_confirmed.send(sender=self.__class__,
                                         request=request,
                                         email_address=email_address)
    verify_email.short_description = "Verify E-mail"


class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'created', 'sent', 'key')
    list_filter = ('sent',)
    raw_id_fields = ('email_address',)


admin.site.register(EmailConfirmation, EmailConfirmationAdmin)
admin.site.register(EmailAddress, EmailAddressAdmin)
