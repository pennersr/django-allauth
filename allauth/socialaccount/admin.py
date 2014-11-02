from django.contrib import admin
from django.utils.functional import allow_lazy
from django import forms

from .models import SocialApp, SocialAccount, SocialToken

from ..account import app_settings
from ..utils import get_user_model, get_possible_search_fields


class SocialAppForm(forms.ModelForm):
    class Meta:
        model = SocialApp
        exclude = []
        widgets = {
            'client_id': forms.TextInput(attrs={'size': '100'}),
            'key': forms.TextInput(attrs={'size': '100'}),
            'secret': forms.TextInput(attrs={'size': '100'})
        }


class SocialAppAdmin(admin.ModelAdmin):
    form = SocialAppForm
    list_display = ('name', 'provider',)
    filter_horizontal = ('sites',)


class SocialAccountAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('user', 'uid', 'provider')
    list_filter = ('provider',)

    @classmethod
    def check(cls, *args, **kwargs):
        """Django 1.7: Silence `list` check for `search_fields.

        Required to silence the check if `ModelAdmin.search_fields` is a list.
        We generate this list dynamically, thus it's working but the check
        framework does not evaluate the expressions and fails.
        """
        errors = super(SocialAccountAdmin, cls).check(*args, **kwargs)

        expected_msg = "The value of 'search_fields' must be a list or tuple."

        def _filter(err):
            if err.id == 'admin.E126' and err.msg == expected_msg:
                return
            return err

        errors = list(filter(_filter, errors))

        return errors

    @classmethod
    def _get_search_fields(cls):
        return get_possible_search_fields(['user__emailaddress__email'])

    search_fields = allow_lazy(_get_search_fields, list)


class SocialTokenAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', 'account',)
    list_display = ('app', 'account', 'truncated_token', 'expires_at')
    list_filter = ('app', 'app__provider', 'expires_at')

    def truncated_token(self, token):
        max_chars = 40
        ret = token.token
        if len(ret) > max_chars:
            ret = ret[0:max_chars] + '...(truncated)'
        return ret
    truncated_token.short_description = 'Token'

admin.site.register(SocialApp, SocialAppAdmin)
admin.site.register(SocialToken, SocialTokenAdmin)
admin.site.register(SocialAccount, SocialAccountAdmin)
