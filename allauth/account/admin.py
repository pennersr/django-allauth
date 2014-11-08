from django.contrib import admin
from django.utils.functional import allow_lazy

from .models import EmailConfirmation, EmailAddress
from . import app_settings
from ..utils import get_user_model, get_possible_search_fields


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'primary', 'verified')
    list_filter = ('primary', 'verified')
    raw_id_fields = ('user',)

    @classmethod
    def check(cls, *args, **kwargs):
        """Django 1.7: Silence `list` check for `search_fields.

        Required to silence the check if `ModelAdmin.search_fields` is a list.
        We generate this list dynamically, thus it's working but the check
        framework does not evaluate the expressions and fails.
        """
        errors = super(EmailAddressAdmin, cls).check(*args, **kwargs)

        expected_msg = "The value of 'search_fields' must be a list or tuple."

        def _filter(err):
            if err.id == 'admin.E126' and err.msg == expected_msg:
                return
            return err

        errors = list(filter(_filter, errors))

        return errors

    @classmethod
    def _get_search_fields(cls):
        return get_possible_search_fields(['email'])

    search_fields = allow_lazy(_get_search_fields, list)


class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'created', 'sent', 'key')
    list_filter = ('sent',)
    raw_id_fields = ('email_address',)


admin.site.register(EmailConfirmation, EmailConfirmationAdmin)
admin.site.register(EmailAddress, EmailAddressAdmin)
