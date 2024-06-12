from typing import List

from django import forms
from django.contrib import admin

from allauth import app_settings
from allauth.account.adapter import get_adapter
from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken


class SocialAppForm(forms.ModelForm):
    class Meta:
        model = SocialApp
        exclude: List[str] = []
        widgets = {
            "client_id": forms.TextInput(attrs={"size": "100"}),
            "key": forms.TextInput(attrs={"size": "100"}),
            "secret": forms.TextInput(attrs={"size": "100"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["provider"] = forms.ChoiceField(
            choices=providers.registry.as_choices()
        )


class SocialAppAdmin(admin.ModelAdmin):
    form = SocialAppForm
    list_display = (
        "name",
        "provider",
    )
    filter_horizontal = ("sites",) if app_settings.SITES_ENABLED else ()


class SocialAccountAdmin(admin.ModelAdmin):
    search_fields = []
    raw_id_fields = ("user",)
    list_display = ("user", "uid", "provider")
    list_filter = ("provider",)

    def get_search_fields(self, request):
        base_fields = get_adapter().get_user_search_fields()
        return list(map(lambda a: "user__" + a, base_fields))


class SocialTokenAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "app",
        "account",
    )
    list_display = ("app", "account", "truncated_token", "expires_at")
    list_filter = ("app", "app__provider", "expires_at")

    def truncated_token(self, token):
        max_chars = 40
        ret = token.token
        if len(ret) > max_chars:
            ret = ret[0:max_chars] + "...(truncated)"
        return ret

    truncated_token.short_description = "Token"  # type: ignore[attr-defined]


admin.site.register(SocialApp, SocialAppAdmin)
admin.site.register(SocialToken, SocialTokenAdmin)
admin.site.register(SocialAccount, SocialAccountAdmin)
