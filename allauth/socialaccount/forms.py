from django.utils.translation import ugettext, ugettext_lazy as _
from django import forms

from emailconfirmation.models import EmailAddress
from models import SocialAccount
from allauth.account.forms import BaseSignupForm
from allauth.account.utils import send_email_confirmation

class SignupForm(BaseSignupForm):

    def save(self, request=None):
        new_user = self.create_user()
        send_email_confirmation(new_user, request=request)
        return new_user


class DisconnectForm(forms.Form):
    account = forms.ModelChoiceField(queryset=SocialAccount.objects.none(),
                                     widget = forms.RadioSelect,
                                     required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.accounts = SocialAccount.objects.filter(user=self.user)
        super(DisconnectForm, self).__init__(*args, **kwargs)
        self.fields['account'].queryset = self.accounts

    def clean(self):
        if len(self.accounts) == 1:
            # No usable password would render the local account unusable
            if not self.user.has_usable_password():
                raise forms.ValidationError(_("Your local account has no password setup."))
            # No email address, no password reset
            if EmailAddress.objects.filter(user=self.user,
                                           verified=True).count() == 0:
                raise forms.ValidationError(_("Your local account has no verified e-mail address."))
        return self.cleaned_data

    def save(self):
        self.cleaned_data['account'].delete()

    

    
