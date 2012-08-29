import re

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.http import int_to_base36
from django.utils.importlib import import_module

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site

from models import EmailAddress

# from models import PasswordReset
from utils import perform_login, send_email_confirmation, format_email_subject
from allauth.utils import email_address_exists, generate_unique_username

from app_settings import AuthenticationMethod
        
import app_settings

alnum_re = re.compile(r"^\w+$")


class PasswordField(forms.CharField):

    def __init__(self, *args, **kwargs):
        render_value = kwargs.pop('render_value', 
                                  app_settings.PASSWORD_INPUT_RENDER_VALUE)
        kwargs['widget'] = forms.PasswordInput(render_value=render_value)
        super(PasswordField, self).__init__(*args, **kwargs)

class SetPasswordField(PasswordField):

    def clean(self, value):
        value = super(SetPasswordField, self).clean(value)
        min_length = app_settings.PASSWORD_MIN_LENGTH
        if len(value) < min_length:
            raise forms.ValidationError(_("Password must be a minimum of {0} "
                                          "characters.").format(min_length))
        return value

class LoginForm(forms.Form):
    
    password = PasswordField(
        label = _("Password"))
    remember = forms.BooleanField(
        label = _("Remember Me"),
        # help_text = _("If checked you will stay logged in for 3 weeks"),
        required = False
    )
    
    user = None
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        if app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.EMAIL:
            login_widget = forms.TextInput(attrs={'placeholder': 
                                                  _('E-mail address') })
            login_field = forms.EmailField(label=_("E-mail"),
                                           widget=login_widget)
        elif app_settings.AUTHENTICATION_METHOD \
                == AuthenticationMethod.USERNAME:
            login_widget = forms.TextInput(attrs={'placeholder': 
                                                  _('Username') })
            login_field = forms.CharField(label=_("Username"),
                                          widget=login_widget,
                                          max_length=30)
        else:
            assert app_settings.AUTHENTICATION_METHOD \
                == AuthenticationMethod.USERNAME_EMAIL
            login_widget = forms.TextInput(attrs={'placeholder': 
                                                  _('Username or e-mail') })
            login_field = forms.CharField(label=ugettext("Login"),
                                          widget=login_widget)
        self.fields["login"] = login_field
        self.fields.keyOrder = ["login", "password", "remember"]
    
    def user_credentials(self):
        """
        Provides the credentials required to authenticate the user for
        login.
        """
        credentials = {}
        login = self.cleaned_data["login"]
        if app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.EMAIL:
            credentials["email"] = login
        elif (app_settings.AUTHENTICATION_METHOD 
              == AuthenticationMethod.USERNAME):
            credentials["username"] = login
        else:
            if "@" in login and "." in login:
                credentials["email"] = login
            else:
                credentials["username"] = login
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
                raise forms.ValidationError(_("This account is currently"
                                              " inactive."))
        else:
            if app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.EMAIL:
                error = _("The e-mail address and/or password you specified"
                          " are not correct.")
            elif app_settings.AUTHENTICATION_METHOD \
                  == AuthenticationMethod.USERNAME:
                error = _("The username and/or password you specified are"
                          " not correct.")
            else:
                error = _("The login and/or password you specified are not"
                          " correct.")
            raise forms.ValidationError(error)
        return self.cleaned_data
    
    def login(self, request, redirect_url=None):
        ret = perform_login(request, self.user, redirect_url=redirect_url)
        if self.cleaned_data["remember"]:
            request.session.set_expiry(60 * 60 * 24 * 7 * 3)
        else:
            request.session.set_expiry(0)
        return ret



class _DummyCustomSignupForm(forms.Form):
    def save(self, user):
        pass

def _base_signup_form_class():
    if not app_settings.SIGNUP_FORM_CLASS:
        return _DummyCustomSignupForm
    try:
        fc_module, fc_classname = app_settings.SIGNUP_FORM_CLASS.rsplit('.', 1)
    except ValueError:
        raise exceptions.ImproperlyConfigured('%s does not point to a form'
                                              ' class' 
                                              % app_settings.SIGNUP_FORM_CLASS)
    try:
        mod = import_module(fc_module)
    except ImportError, e:
        raise exceptions.ImproperlyConfigured('Error importing form class %s:'
                                              ' "%s"' % (fc_module, e))
    try:
        fc_class = getattr(mod, fc_classname)
    except AttributeError:
        raise exceptions.ImproperlyConfigured('Module "%s" does not define a'
                                              ' "%s" class' % (fc_module, 
                                                               fc_classname))
    if not hasattr(fc_class, 'save'):
        raise exceptions.ImproperlyConfigured('The custom signup form must'
                                              ' implement a "save" method')
    return fc_class

                                             
class BaseSignupForm(_base_signup_form_class()):
    username = forms.CharField(
        label = _("Username"),
        max_length = 30,
        widget = forms.TextInput()
    )
    email = forms.EmailField(widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super(BaseSignupForm, self).__init__(*args, **kwargs)
        if (app_settings.EMAIL_REQUIRED or 
            app_settings.EMAIL_VERIFICATION or
            app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.EMAIL):
            self.fields["email"].label = ugettext("E-mail")
            self.fields["email"].required = True
        else:
            self.fields["email"].label = ugettext("E-mail (optional)")
            self.fields["email"].required = False
        if not app_settings.USERNAME_REQUIRED:
            del self.fields["username"]

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
        if app_settings.UNIQUE_EMAIL:
            if value and email_address_exists(value):
                raise forms.ValidationError \
                    (_("A user is registered with this e-mail address."))
        return value
    
    def create_user(self, commit=True):
        user = User()
        # data collected by providers, if any, is passed as `initial`
        # signup form data. This may contain fields such as
        # `first_name`, whereas these may not have field counterparts
        # in the form itself. So let's pick these up here...
        data = self.initial
        user.last_name = data.get('last_name', '')
        user.first_name = data.get('first_name', '')
        user.email = self.cleaned_data["email"].strip().lower()
        if app_settings.USERNAME_REQUIRED:
            user.username = self.cleaned_data["username"]
        else:
            user.username = generate_unique_username(user.first_name or
                                                     user.last_name or
                                                     user.email)
        user.set_unusable_password()
        if commit:
            user.save()
        return user


class SignupForm(BaseSignupForm):
    
    password1 = SetPasswordField(label=_("Password"))
    password2 = PasswordField(label=_("Password (again)"))
    confirmation_key = forms.CharField(
        max_length = 40,
        required = False,
        widget = forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        current_order =self.fields.keyOrder
        preferred_order = self.fields.keyOrder = ["username", 
                                                  "password1", 
                                                  "password2",
                                                  "email"]
        if not app_settings.USERNAME_REQUIRED:
            preferred_order = self.fields.keyOrder = ["email",
                                                      "password1", 
                                                      "password2"]
        # Make sure custom fields are put below main signup fields
        self.fields.keyOrder = preferred_order + [ f for f in current_order if not f in preferred_order ]
        if not app_settings.SIGNUP_PASSWORD_VERIFICATION:
            del self.fields["password2"]
    
    def clean(self):
        super(SignupForm, self).clean()
        if app_settings.SIGNUP_PASSWORD_VERIFICATION \
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
        
        new_user = self.create_user()
        super(SignupForm, self).save(new_user)

        # @@@ clean up some of the repetition below -- DRY!
        if confirmed:
            if email == join_invitation.contact.email:
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                if request:
                    messages.add_message(request, messages.INFO,
                        ugettext(u"Your e-mail address has already been verified")
                    )
                # already verified so can just create
                EmailAddress(user=new_user, email=email, verified=True, primary=True).save()
            else:
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
        if app_settings.UNIQUE_EMAIL:
            if emails.exclude(user=self.user).exists():
                raise forms.ValidationError(errors["different_account"])
        return value
    
    def save(self):
        return EmailAddress.objects.add_email(self.user, 
                                              self.cleaned_data["email"],
                                              confirm=True)


class ChangePasswordForm(UserForm):
    
    oldpassword = PasswordField(label=_("Current Password"))
    password1 = SetPasswordField(label=_("New Password"))
    password2 = PasswordField(label=_("New Password (again)"))
    
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
    
    password1 = SetPasswordField(label=_("Password"))
    password2 = PasswordField(label=_("Password (again)"))
    
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

            # send the password reset email
            subject = format_email_subject(_("Password Reset E-mail"))
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
    
    password1 = SetPasswordField(label=_("New Password"))
    password2 = PasswordField(label=_("New Password (again)"))
    
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


