from django import forms
from django.utils.html import mark_safe


class LoginForm(forms.Form):
    openid = forms.URLField(
        label=("OpenID"),
        help_text=mark_safe(
            'Get an <a href="http://openidexplained.com/get">OpenID</a>'
        ),
    )
    next = forms.CharField(widget=forms.HiddenInput, required=False)
    process = forms.CharField(widget=forms.HiddenInput, required=False)
