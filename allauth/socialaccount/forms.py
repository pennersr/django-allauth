from __future__ import absolute_import

from django import forms
from django.utils.translation import ugettext_lazy as _

from allauth.account.forms import BaseSignupForm

from .models import SocialAccount
from .adapter import get_adapter
from . import app_settings
from . import signals


class SignupForm(BaseSignupForm):

    def __init__(self, *args, **kwargs):
        self.sociallogin = kwargs.pop('sociallogin')
        initial = get_adapter().get_signup_form_initial_data(
            self.sociallogin)
        kwargs.update({
            'initial': initial,
            'email_required': kwargs.get('email_required',
                                         app_settings.EMAIL_REQUIRED)})
        super(SignupForm, self).__init__(*args, **kwargs)

    def save(self, request):
        adapter = get_adapter(request)
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
            get_adapter(self.request).validate_disconnect(
                account,
                self.accounts)
        return cleaned_data

    def save(self):
        account = self.cleaned_data['account']
        account.delete()
        signals.social_account_removed.send(sender=SocialAccount,
                                            request=self.request,
                                            socialaccount=account)
