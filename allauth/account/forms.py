import base64
import re
import uuid

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.encoding import smart_unicode
from django.utils.hashcompat import sha_constructor
from django.utils.http import int_to_base36

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site

from emailconfirmation.models import EmailAddress

# from models import PasswordReset
from utils import user_display, perform_login, send_email_confirmation
from allauth.utils import email_address_exists
        
from app_settings import *

alnum_re = re.compile(r"^\w+$")


class LoginForm(forms.Form):
    
    password = forms.CharField(
        label = _("Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    remember = forms.BooleanField(
        label = _("Remember Me"),
        # help_text = _("If checked you will stay logged in for 3 weeks"),
        required = False
    )
    
    user = None
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        ordering = []
        if EMAIL_AUTHENTICATION:
            self.fields["email"] = forms.EmailField(
                label = ugettext("E-mail"),
            )
            ordering.append("email")
        else:
            self.fields["username"] = forms.CharField(
                label = ugettext("Username"),
                max_length = 30,
            )
            ordering.append("username")
        ordering.extend(["password", "remember"])
        self.fields.keyOrder = ordering
    
    def user_credentials(self):
        """
        Provides the credentials required to authenticate the user for
        login.
        """
        credentials = {}
        if EMAIL_AUTHENTICATION:
            credentials["email"] = self.cleaned_data["email"]
        else:
            credentials["username"] = self.cleaned_data["username"]
        credentials["password"] = self.cleaned_data["password"]
        return credentials
    
    def clean(self):
        if self._errors:
            return
        user = authenticate(**self.user_credentials())
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValidationError(_("This account is currently inactive."))
        else:
            if EMAIL_AUTHENTICATION:
                error = _("The e-mail address and/or password you specified are not correct.")
            else:
                error = _("The username and/or password you specified are not correct.")
            raise forms.ValidationError(error)
        return self.cleaned_data
    
    def login(self, request):
        perform_login(request, self.user)
        if self.cleaned_data["remember"]:
            request.session.set_expiry(60 * 60 * 24 * 7 * 3)
        else:
            request.session.set_expiry(0)


class BaseSignupForm(forms.Form):
    username = forms.CharField(
        label = _("Username"),
        max_length = 30,
        widget = forms.TextInput()
    )
    email = forms.EmailField(widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super(BaseSignupForm, self).__init__(*args, **kwargs)
        if EMAIL_REQUIRED or EMAIL_VERIFICATION or EMAIL_AUTHENTICATION:
            self.fields["email"].label = ugettext("E-mail")
            self.fields["email"].required = True
        else:
            self.fields["email"].label = ugettext("E-mail (optional)")
            self.fields["email"].required = False
        if not USERNAME_REQUIRED:
            del self.fields["username"]

    def random_username(self):
        return base64.urlsafe_b64encode(uuid.uuid4().bytes).strip('=')

    def clean_username(self):
        value = self.cleaned_data["username"]
        if not alnum_re.search(value):
            raise forms.ValidationError(_("Usernames can only contain "
                                          "letters, numbers and underscores."))
        try:
            User.objects.get(username__iexact=value)
        except User.DoesNotExist:
            return value
        raise forms.ValidationError(_("This username is already taken. Please "
                                      "choose another."))
    
    def clean_email(self):
        value = self.cleaned_data["email"]
        if UNIQUE_EMAIL or EMAIL_AUTHENTICATION:
            if value and email_address_exists(value):
                raise forms.ValidationError \
                    (_("A user is registered with this e-mail address."))
        return value
    
    def create_user(self, commit=True):
        user = User()
        if USERNAME_REQUIRED:
            user.username = self.cleaned_data["username"]
        else:
            while True:
                user.username = self.random_username()
                try:
                    User.objects.get(username=user.username)
                except User.DoesNotExist:
                    break
        user.email = self.cleaned_data["email"].strip().lower()
        user.set_unusable_password()
        if EMAIL_VERIFICATION:
            user.is_active = False
        if commit:
            user.save()
        return user


class SignupForm(BaseSignupForm):
    
    password1 = forms.CharField(
        label = _("Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
	label = _("Password (again)"),
	widget = forms.PasswordInput(render_value=False)
    )
    confirmation_key = forms.CharField(
        max_length = 40,
        required = False,
        widget = forms.HiddenInput()
    )
    
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ["username", 
                                "password1", 
                                "password2",
                                "email"]
        if not USERNAME_REQUIRED:
            self.fields.keyOrder = ["email",
                                    "password1", 
                                    "password2"]
        if not SIGNUP_PASSWORD_VERIFICATION:
            del self.fields["password2"]
    
    def clean(self):
        if SIGNUP_PASSWORD_VERIFICATION \
                and "password1" in self.cleaned_data \
                and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data
    
    def create_user(self, commit=True):
        user = super(SignupForm, self).create_user(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
    
    def save(self, request=None):
        # don't assume a username is available. it is a common removal if
        # site developer wants to use e-mail authentication.
        username = self.cleaned_data.get("username")
        email = self.cleaned_data["email"]
        
        if self.cleaned_data.get("confirmation_key"):
            from friends.models import JoinInvitation # @@@ temporary fix for issue 93
            try:
                join_invitation = JoinInvitation.objects.get(confirmation_key=self.cleaned_data["confirmation_key"])
                confirmed = True
            except JoinInvitation.DoesNotExist:
                confirmed = False
        else:
            confirmed = False
        
        # @@@ clean up some of the repetition below -- DRY!
        
        if confirmed:
            if email == join_invitation.contact.email:
                new_user = self.create_user()
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                if request:
                    messages.add_message(request, messages.INFO,
                        ugettext(u"Your e-mail address has already been verified")
                    )
                # already verified so can just create
                EmailAddress(user=new_user, email=email, verified=True, primary=True).save()
            else:
                new_user = self.create_user()
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                if email:
                    if request:
                        messages.add_message(request, messages.INFO,
                            ugettext(u"Confirmation e-mail sent to %(email)s") % {
                                "email": email,
                            }
                        )
                    EmailAddress.objects.add_email(new_user, email)
        else:
            new_user = self.create_user()
            send_email_confirmation(new_user, request=request)
        
        self.after_signup(new_user)
        
        return new_user
    
    def after_signup(self, user, **kwargs):
        """
        An extension point for subclasses.
        """
        pass


class UserForm(forms.Form):
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)


class AccountForm(UserForm):
    
    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        try:
            self.account = Account.objects.get(user=self.user)
        except Account.DoesNotExist:
            self.account = Account(user=self.user)


class AddEmailForm(UserForm):
    
    email = forms.EmailField(
        label = _("E-mail"),
        required = True,
        widget = forms.TextInput(attrs={"size": "30"})
    )
    
    def clean_email(self):
        value = self.cleaned_data["email"]
        errors = {
            "this_account": _("This e-mail address already associated with this account."),
            "different_account": _("This e-mail address already associated with another account."),
        }
        emails = EmailAddress.objects.filter(email__iexact=value)
        if emails.filter(user=self.user).exists():
            raise forms.ValidationError(errors["this_account"])
        if UNIQUE_EMAIL:
            if emails.exclude(user=self.user).exists():
                raise forms.ValidationError(errors["different_account"])
        return value
    
    def save(self):
        return EmailAddress.objects.add_email(self.user, self.cleaned_data["email"])


class ChangePasswordForm(UserForm):
    
    oldpassword = forms.CharField(
        label = _("Current Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    password1 = forms.CharField(
        label = _("New Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label = _("New Password (again)"),
        widget = forms.PasswordInput(render_value=False)
    )
    
    def clean_oldpassword(self):
        if not self.user.check_password(self.cleaned_data.get("oldpassword")):
            raise forms.ValidationError(_("Please type your current password."))
        return self.cleaned_data["oldpassword"]
    
    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]
    
    def save(self):
        self.user.set_password(self.cleaned_data["password1"])
        self.user.save()


class SetPasswordForm(UserForm):
    
    password1 = forms.CharField(
        label = _("Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label = _("Password (again)"),
        widget = forms.PasswordInput(render_value=False)
    )
    
    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]
    
    def save(self):
        self.user.set_password(self.cleaned_data["password1"])
        self.user.save()


class ResetPasswordForm(forms.Form):
    
    email = forms.EmailField(
        label = _("E-mail"),
        required = True,
        widget = forms.TextInput(attrs={"size":"30"})
    )
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        self.users = User.objects.filter(Q(email__iexact=email)
                                         | Q(emailaddress__email__iexact=email)).distinct()
        if not self.users.exists():
            raise forms.ValidationError(_("The e-mail address is not assigned to any user account"))
        return self.cleaned_data["email"]
    
    def save(self, **kwargs):
        
        email = self.cleaned_data["email"]
        token_generator = kwargs.get("token_generator", default_token_generator)
        
        for user in self.users:
            
            temp_key = token_generator.make_token(user)
            
            # save it to the password reset model
            # password_reset = PasswordReset(user=user, temp_key=temp_key)
            # password_reset.save()
            
            current_site = Site.objects.get_current()
            domain = unicode(current_site.domain)
            
            # send the password reset email
            subject = _("Password Reset E-mail")
            path = reverse("account_reset_password_from_key",
                           kwargs=dict(uidb36=int_to_base36(user.id),
                                       key=temp_key))
            url = 'http://%s%s' % (current_site.domain,
                                   path)
            message = render_to_string \
                ("account/password_reset_key_message.txt", 
                 { "site": current_site,
                   "user": user,
                   "password_reset_url": url })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        return self.cleaned_data["email"]


class ResetPasswordKeyForm(forms.Form):
    
    password1 = forms.CharField(
        label = _("New Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label = _("New Password (again)"),
        widget = forms.PasswordInput(render_value=False)
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.temp_key = kwargs.pop("temp_key", None)
        super(ResetPasswordKeyForm, self).__init__(*args, **kwargs)
    
    # FIXME: Inspecting other fields -> should be put in def clean(self) ?
    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]
    
    def save(self):
        # set the new user password
        user = self.user
        user.set_password(self.cleaned_data["password1"])
        user.save()
        # mark password reset object as reset
        # PasswordReset.objects.filter(temp_key=self.temp_key).update(reset=True)


