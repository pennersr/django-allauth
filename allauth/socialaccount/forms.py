from django.utils.translation import ugettext, ugettext_lazy as _
from django import forms

from emailconfirmation.models import EmailAddress
from models import SocialAccount

class SetupForm(forms.Form):
    username = forms.RegexField \
        (label=_("Username"), 
         max_length=30, 
         regex=r'^[\w.@+-]+$',
         help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
         error_messages = {'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    email = forms.EmailField(required=False)

    def __init__(self, user, profile, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.user = user
        self.profile = profile

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            user = User.objects.get(username=username)
            raise forms.ValidationError(_('This username is already in use.'))
        except User.DoesNotExist:
            return username

    def save(self, request=None):
        self.user.username = self.cleaned_data.get('username')
        self.user.email = self.cleaned_data.get('email')
        self.user.save()
        self.profile.user = self.user
        self.profile.save()
        return self.user

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
                raise forms.ValidationError(_("Your local account has no password  setup."))
            # No email address, no password reset
            if EmailAddress.objects.filter(user=self.user,
                                           verified=True).count() == 0:
                raise forms.ValidationError(_("Your local account has no verified e-mail address."))
        return self.cleaned_data

    def save(self):
        self.cleaned_data['account'].delete()

    

    
