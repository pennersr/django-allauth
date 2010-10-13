from django.utils.translation import ugettext, ugettext_lazy as _
from django import forms


class LoginForm(forms.Form):
    openid = forms.URLField(label=_('OpenID'),
                            help_text='Get an <a href="http://openid.net/get-an-openid/">OpenID</a>')
