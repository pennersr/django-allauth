from __future__ import absolute_import

import warnings

from django import forms
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.utils.translation import pgettext, ugettext_lazy as _, ugettext

from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator

from ..utils import (email_address_exists,
                     set_form_field_order,
                     build_absolute_uri,
                     get_username_max_length,
                     get_current_site)

from .models import EmailAddress
from .utils import (perform_login, setup_user_email, url_str_to_user_pk,
                    user_username, user_pk_to_url_str, filter_users_by_email,
                    get_user_model)
from .app_settings import AuthenticationMethod
from . import app_settings
from .adapter import get_adapter

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module


class PasswordField(forms.CharField):

    def __init__(self, *args, **kwargs):
        render_value = kwargs.pop('render_value',
                                  app_settings.PASSWORD_INPUT_RENDER_VALUE)
        kwargs['widget'] = forms.PasswordInput(render_value=render_value,
                                               attrs={'placeholder':
                                                      _(kwargs.get("label"))})
        super(PasswordField, self).__init__(*args, **kwargs)


class SetPasswordField(PasswordField):

    def clean(self, value):
        value = super(SetPasswordField, self).clean(value)
        value = get_adapter().clean_password(value)
        return value


class LoginForm(forms.Form):

    password = PasswordField(label=_("Password"))
    remember = forms.BooleanField(label=_("Remember Me"),
                                  required=False)

    user = None
    error_messages = {
        'account_inactive':
        _("This account is currently inactive."),

        'email_password_mismatch':
        _("The e-mail address and/or password you specified are not correct."),

        'username_password_mismatch':
        _("The username and/or password you specified are not correct."),

        'username_email_password_mismatch':
        _("The login and/or password you specified are not correct.")
    }

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        if app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.EMAIL:
            login_widget = forms.TextInput(attrs={'type': 'email',
                                                  'placeholder':
                                                  _('E-mail address'),
                                                  'autofocus': 'autofocus'})
            login_field = forms.EmailField(label=_("E-mail"),
                                           widget=login_widget)
        elif app_settings.AUTHENTICATION_METHOD \
                == AuthenticationMethod.USERNAME:
            login_widget = forms.TextInput(attrs={'placeholder':
                                                  _('Username'),
                                                  'autofocus': 'autofocus'})
            login_field = forms.CharField(
                label=_("Username"),
                widget=login_widget,
                max_length=get_username_max_length())
        else:
            assert app_settings.AUTHENTICATION_METHOD \
                == AuthenticationMethod.USERNAME_EMAIL
            login_widget = forms.TextInput(attrs={'placeholder':
                                                  _('Username or e-mail'),
                                                  'autofocus': 'autofocus'})
            login_field = forms.CharField(label=pgettext("field label",
                                                         "Login"),
                                          widget=login_widget)
        self.fields["login"] = login_field
        set_form_field_order(self,  ["login", "password", "remember"])
        if app_settings.SESSION_REMEMBER is not None:
            del self.fields['remember']

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
            credentials["username"] = login
        credentials["password"] = self.cleaned_data["password"]
        return credentials

    def clean_login(self):
        login = self.cleaned_data['login']
        return login.strip()

    def clean(self):
        if self._errors:
            return
        user = authenticate(**self.user_credentials())
        if user:
            self.user = user
        else:
            raise forms.ValidationError(
                self.error_messages[
                    '%s_password_mismatch'
                    % app_settings.AUTHENTICATION_METHOD])
        return self.cleaned_data

    def login(self, request, redirect_url=None):
        ret = perform_login(request, self.user,
                            email_verification=app_settings.EMAIL_VERIFICATION,
                            redirect_url=redirect_url)
        remember = app_settings.SESSION_REMEMBER
        if remember is None:
            remember = self.cleaned_data['remember']
        if remember:
            request.session.set_expiry(app_settings.SESSION_COOKIE_AGE)
        else:
            request.session.set_expiry(0)
        return ret


class _DummyCustomSignupForm(forms.Form):

    def signup(self, request, user):
        """
        Invoked at signup time to complete the signup of the user.
        """
        pass


def _base_signup_form_class():
    """
    Currently, we inherit from the custom form, if any. This is all
    not very elegant, though it serves a purpose:

    - There are two signup forms: one for local accounts, and one for
      social accounts
    - Both share a common base (BaseSignupForm)

    - Given the above, how to put in a custom signup form? Which form
      would your custom form derive from, the local or the social one?
    """
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
    except ImportError as e:
        raise exceptions.ImproperlyConfigured('Error importing form class %s:'
                                              ' "%s"' % (fc_module, e))
    try:
        fc_class = getattr(mod, fc_classname)
    except AttributeError:
        raise exceptions.ImproperlyConfigured('Module "%s" does not define a'
                                              ' "%s" class' % (fc_module,
                                                               fc_classname))
    if not hasattr(fc_class, 'signup'):
        if hasattr(fc_class, 'save'):
            warnings.warn("The custom signup form must offer"
                          " a `def signup(self, request, user)` method",
                          DeprecationWarning)
        else:
            raise exceptions.ImproperlyConfigured(
                'The custom signup form must implement a "signup" method')
    return fc_class


class BaseSignupForm(_base_signup_form_class()):
    username = forms.CharField(label=_("Username"),
                               max_length=get_username_max_length(),
                               min_length=app_settings.USERNAME_MIN_LENGTH,
                               widget=forms.TextInput(
                                   attrs={'placeholder':
                                          _('Username'),
                                          'autofocus': 'autofocus'}))
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'type': 'email',
               'placeholder': _('E-mail address')}))

    def __init__(self, *args, **kwargs):
        email_required = kwargs.pop('email_required',
                                    app_settings.EMAIL_REQUIRED)
        self.username_required = kwargs.pop('username_required',
                                            app_settings.USERNAME_REQUIRED)
        super(BaseSignupForm, self).__init__(*args, **kwargs)
        # field order may contain additional fields from our base class,
        # so take proper care when reordering...
        field_order = ['email', 'username']
        merged_field_order = list(self.fields.keys())
        if email_required:
            self.fields["email"].label = ugettext("E-mail")
            self.fields["email"].required = True
        else:
            self.fields["email"].label = ugettext("E-mail (optional)")
            self.fields["email"].required = False
            self.fields["email"].widget.is_required = False
            if self.username_required:
                field_order = ['username', 'email']

        # Merge our email and username fields in if they are not
        # currently in the order.  This is to allow others to
        # re-arrange email and username if they desire.  Go in reverse
        # so that we make sure the inserted items are always
        # prepended.
        for field in reversed(field_order):
            if field not in merged_field_order:
                merged_field_order.insert(0, field)
        set_form_field_order(self, merged_field_order)
        if not self.username_required:
            del self.fields["username"]

    def clean_username(self):
        value = self.cleaned_data["username"]
        value = get_adapter().clean_username(value)
        return value

    def clean_email(self):
        value = self.cleaned_data["email"]
        value = get_adapter().clean_email(value)
        if app_settings.UNIQUE_EMAIL:
            if value and email_address_exists(value):
                self.raise_duplicate_email_error()
        return value

    def raise_duplicate_email_error(self):
        raise forms.ValidationError(_("A user is already registered"
                                      " with this e-mail address."))

    def custom_signup(self, request, user):
        custom_form = super(BaseSignupForm, self)
        if hasattr(custom_form, 'signup') and callable(custom_form.signup):
            custom_form.signup(request, user)
        else:
            warnings.warn("The custom signup form must offer"
                          " a `def signup(self, request, user)` method",
                          DeprecationWarning)
            # Historically, it was called .save, but this is confusing
            # in case of ModelForm
            custom_form.save(user)


class SignupForm(BaseSignupForm):

    password1 = SetPasswordField(label=_("Password"))
    password2 = PasswordField(label=_("Password (again)"))
    confirmation_key = forms.CharField(max_length=40,
                                       required=False,
                                       widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        if not app_settings.SIGNUP_PASSWORD_VERIFICATION:
            del self.fields["password2"]

    def clean(self):
        super(SignupForm, self).clean()
        if app_settings.SIGNUP_PASSWORD_VERIFICATION \
                and "password1" in self.cleaned_data \
                and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] \
                    != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password"
                                              " each time."))
        return self.cleaned_data

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        # TODO: Move into adapter `save_user` ?
        setup_user_email(request, user, [])
        return user


class UserForm(forms.Form):

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)


class AddEmailForm(UserForm):

    email = forms.EmailField(label=_("E-mail"),
                             required=True,
                             widget=forms.TextInput(attrs={"type": "email",
                                                            "size": "30",
                                                            "placeholder": _('E-mail address')}))

    def clean_email(self):
        value = self.cleaned_data["email"]
        value = get_adapter().clean_email(value)
        errors = {
            "this_account": _("This e-mail address is already associated"
                              " with this account."),
            "different_account": _("This e-mail address is already associated"
                                   " with another account."),
        }
        users = filter_users_by_email(value)
        on_this_account = [u for u in users if u.pk == self.user.pk]
        on_diff_account = [u for u in users if u.pk != self.user.pk]

        if on_this_account:
            raise forms.ValidationError(errors["this_account"])
        if on_diff_account and app_settings.UNIQUE_EMAIL:
            raise forms.ValidationError(errors["different_account"])
        return value

    def save(self, request):
        return EmailAddress.objects.add_email(request,
                                              self.user,
                                              self.cleaned_data["email"],
                                              confirm=True)


class ChangePasswordForm(UserForm):

    oldpassword = PasswordField(label=_("Current Password"))
    password1 = SetPasswordField(label=_("New Password"))
    password2 = PasswordField(label=_("New Password (again)"))

    def clean_oldpassword(self):
        if not self.user.check_password(self.cleaned_data.get("oldpassword")):
            raise forms.ValidationError(_("Please type your current"
                                          " password."))
        return self.cleaned_data["oldpassword"]

    def clean_password2(self):
        if ("password1" in self.cleaned_data
                and "password2" in self.cleaned_data):
            if (self.cleaned_data["password1"]
                    != self.cleaned_data["password2"]):
                raise forms.ValidationError(_("You must type the same password"
                                              " each time."))
        return self.cleaned_data["password2"]

    def save(self):
        get_adapter().set_password(self.user, self.cleaned_data["password1"])


class SetPasswordForm(UserForm):

    password1 = SetPasswordField(label=_("Password"))
    password2 = PasswordField(label=_("Password (again)"))

    def clean_password2(self):
        if ("password1" in self.cleaned_data
                and "password2" in self.cleaned_data):
            if (self.cleaned_data["password1"]
                    != self.cleaned_data["password2"]):
                raise forms.ValidationError(_("You must type the same password"
                                              " each time."))
        return self.cleaned_data["password2"]

    def save(self):
        get_adapter().set_password(self.user, self.cleaned_data["password1"])


class ResetPasswordForm(forms.Form):

    email = forms.EmailField(
        label=_("E-mail"),
        required=True,
        widget=forms.TextInput(attrs={"type": "email", "size": "30"}))

    def clean_email(self):
        email = self.cleaned_data["email"]
        email = get_adapter().clean_email(email)
        self.users = filter_users_by_email(email)
        if not self.users:
            raise forms.ValidationError(_("The e-mail address is not assigned"
                                          " to any user account"))
        return self.cleaned_data["email"]

    def save(self, request, **kwargs):

        email = self.cleaned_data["email"]
        token_generator = kwargs.get("token_generator",
                                     default_token_generator)

        for user in self.users:

            temp_key = token_generator.make_token(user)

            # save it to the password reset model
            # password_reset = PasswordReset(user=user, temp_key=temp_key)
            # password_reset.save()

            current_site = get_current_site(request)

            # send the password reset email
            path = reverse("account_reset_password_from_key",
                           kwargs=dict(uidb36=user_pk_to_url_str(user),
                                       key=temp_key))
            url = build_absolute_uri(
                request, path,
                protocol=app_settings.DEFAULT_HTTP_PROTOCOL)
            context = {"site": current_site,
                       "user": user,
                       "password_reset_url": url,
                       "request": request}
            if app_settings.AUTHENTICATION_METHOD \
                    != AuthenticationMethod.EMAIL:
                context['username'] = user_username(user)
            get_adapter().send_mail('account/email/password_reset_key',
                                    email,
                                    context)
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
        if ("password1" in self.cleaned_data
                and "password2" in self.cleaned_data):
            if (self.cleaned_data["password1"]
                    != self.cleaned_data["password2"]):
                raise forms.ValidationError(_("You must type the same"
                                              " password each time."))
        return self.cleaned_data["password2"]

    def save(self):
        get_adapter().set_password(self.user, self.cleaned_data["password1"])


class UserTokenForm(forms.Form):

    uidb36 = forms.CharField()
    key = forms.CharField()

    reset_user = None
    token_generator = default_token_generator

    error_messages = {
        'token_invalid': _('The password reset token was invalid.'),
    }

    def _get_user(self, uidb36):
        User = get_user_model()
        try:
            pk = url_str_to_user_pk(uidb36)
            return User.objects.get(pk=pk)
        except (ValueError, User.DoesNotExist):
            return None

    def clean(self):
        cleaned_data = super(UserTokenForm, self).clean()

        uidb36 = cleaned_data['uidb36']
        key = cleaned_data['key']

        self.reset_user = self._get_user(uidb36)
        if (self.reset_user is None or
                not self.token_generator.check_token(self.reset_user, key)):
            raise forms.ValidationError(self.error_messages['token_invalid'])

        return cleaned_data
