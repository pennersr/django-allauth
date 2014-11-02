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

    @staticmethod
    def _get_search_fields():
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
