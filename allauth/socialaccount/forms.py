from __future__ import absolute_import

from django import forms
from django.utils.translation import ugettext_lazy as _

from allauth.account.forms import BaseSignupForm
from allauth.account.utils import (user_username, user_email,
                                   user_field)

from .models import SocialAccount
from .adapter import get_adapter
from . import app_settings
from . import signals


class SignupForm(BaseSignupForm):

    def __init__(self, *args, **kwargs):
        self.sociallogin = kwargs.pop('sociallogin')
        user = self.sociallogin.user
        # TODO: Should become more generic, not listing
        # a few fixed properties.
        initial = {'email': user_email(user) or '',
                   'username': user_username(user) or '',
                   'first_name': user_field(user, 'first_name') or '',
                   'last_name': user_field(user, 'last_name') or ''}
        kwargs.update({
            'initial': initial,
            'email_required': kwargs.get('email_required',
                                         app_settings.EMAIL_REQUIRED)})
        super(SignupForm, self).__init__(*args, **kwargs)

    def save(self, request):
        adapter = get_adapter()
        user = adapter.save_user(request, self.sociallogin, form=self)
        self.custom_signup(request, user)
        return user

    def raise_duplicate_email_error(self):
        raise forms.ValidationError(
            _("An account already exists with this e-mail address."
              " Please sign in to that account first, then connect"
              " your %s account.")
            % self.sociallogin.account.get_provider().name)


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
