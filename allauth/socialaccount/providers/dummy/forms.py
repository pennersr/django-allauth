from django import forms

from allauth.account.fields import EmailField


class AuthenticateForm(forms.Form):
    id = forms.IntegerField(label="Account ID")
    email = EmailField(required=False)
    email_verified = forms.BooleanField(required=False)
    username = forms.CharField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
