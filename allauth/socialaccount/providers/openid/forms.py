
from django import forms


class LoginForm(forms.Form):
    openid = forms.URLField(
        label=('OpenID'),
        help_text=(
            'Get an <a href="http://openid.net/get-an-openid/">OpenID</a>'))
    next = forms.CharField(
        widget=forms.HiddenInput,
        required=False)
    process = forms.CharField(
        widget=forms.HiddenInput,
        required=False)
