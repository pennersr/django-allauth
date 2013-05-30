from __future__ import absolute_import

from django import forms

from allauth.account.forms import BaseSignupForm
from allauth.account.utils import (send_email_confirmation,
                                   user_username, user_email)

from .models import SocialAccount
from .adapter import get_adapter
from . import app_settings
from . import signals

class SignupForm(BaseSignupForm):

    def __init__(self, *args, **kwargs):
        self.sociallogin = kwargs.pop('sociallogin')
        user = self.sociallogin.account.user
        initial = { 'email': user_email(user) or '',
                    'username': user_username(user) or '',
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '' }
        kwargs['initial'] = initial
        kwargs['email_required'] = app_settings.EMAIL_REQUIRED
        super(SignupForm, self).__init__(*args, **kwargs)

    def save(self, request):
        new_user = self.create_user()
        self.sociallogin.account.user = new_user
        self.sociallogin.save(request)
        super(SignupForm, self).save(new_user) 
        # Confirmation last (save may alter first_name etc -- used in mail)
        send_email_confirmation(request, new_user)
        return new_user


class DisconnectForm(forms.Form):
    account = forms.ModelChoiceField(queryset=SocialAccount.objects.none(),
                                     widget=forms.RadioSelect,
                                     required=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.accounts = SocialAccount.objects.filter(user=self.request.user)
        super(DisconnectForm, self).__init__(*args, **kwargs)
        self.fields['account'].queryset = self.accounts

    def clean(self):
        cleaned_data = super(DisconnectForm, self).clean()
        account = cleaned_data.get('account')
        if account:
            get_adapter().validate_disconnect(account, self.accounts)
        return cleaned_data

    def save(self):
        account = self.cleaned_data['account']
        account.delete()
        signals.social_account_removed.send(sender=SocialAccount,
                                            request=self.request, 
                                            socialaccount=account)
