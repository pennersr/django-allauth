
from django import forms


class LoginForm(forms.Form):
    openid = forms.URLField(label=('OpenID'),
                            help_text='Get an <a href="http://openid.net/get-an-openid/">OpenID</a>')
