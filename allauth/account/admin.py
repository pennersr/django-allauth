from django.contrib import admin
from django.utils.functional import allow_lazy

from .models import EmailConfirmation, EmailAddress
from . import app_settings
from ..utils import get_user_model, get_possible_search_fields


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'primary', 'verified')
    list_filter = ('primary', 'verified')
    raw_id_fields = ('user',)

    @staticmethod
    def _get_search_fields():
        return get_possible_search_fields(['email'])

    search_fields = allow_lazy(_get_search_fields, list)


class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'created', 'sent', 'key')
    list_filter = ('sent',)
    raw_id_fields = ('email_address',)


admin.site.register(EmailConfirmation, EmailConfirmationAdmin)
admin.site.register(EmailAddress, EmailAddressAdmin)
