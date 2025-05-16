from django import forms
from django.forms import widgets
from django.utils.translation import gettext as _

from allauth.idp.oidc.adapter import get_adapter


class AuthorizeForm(forms.Form):
    request = forms.CharField(widget=widgets.HiddenInput)

    def __init__(self, *args, **kwargs):
        requested_scopes = kwargs.pop("requested_scopes")
        super().__init__(*args, **kwargs)
        adapter = get_adapter()
        choices = [(rs, adapter.scope_display.get(rs, rs)) for rs in requested_scopes]
        choices = sorted(choices, key=lambda ch: ch[1])
        self.fields["scopes"] = forms.MultipleChoiceField(
            choices=choices,
            label=_("Grant permissions"),
            widget=forms.CheckboxSelectMultiple,
            initial=requested_scopes,
            required=True,
        )
