from importlib import import_module

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core import exceptions, validators
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _, pgettext

from ..utils import (
    build_absolute_uri,
    get_username_max_length,
    set_form_field_order,
)
from . import app_settings
from .adapter import get_adapter
from .app_settings import AuthenticationMethod
from .models import EmailAddress
from .utils import (
    assess_unique_email,
    filter_users_by_email,
    get_user_model,
    perform_login,
    setup_user_email,
    sync_user_email_addresses,
    url_str_to_user_pk,
    user_email,
    user_pk_to_url_str,
    user_username,
)


class EmailAwarePasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        ret = super(EmailAwarePasswordResetTokenGenerator, self)._make_hash_value(
            user, timestamp
        )
        sync_user_email_addresses(user)
        email = user_email(user)
        emails = set([email] if email else [])
        emails.update(
            EmailAddress.objects.filter(user=user).values_list("email", flat=True)
        )
        ret += "|".join(sorted(emails))
        return ret


default_token_generator = app_settings.PASSWORD_RESET_TOKEN_GENERATOR()


class PasswordVerificationMixin(object):
    def clean(self):
        cleaned_data = super(PasswordVerificationMixin, self).clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if (password1 and password2) and password1 != password2:
            self.add_error("password2", _("You must type the same password each time."))
        return cleaned_data


class PasswordField(forms.CharField):
    def __init__(self, *args, **kwargs):
        render_value = kwargs.pop(
            "render_value", app_settings.PASSWORD_INPUT_RENDER_VALUE
        )
        kwargs["widget"] = forms.PasswordInput(
            render_value=render_value,
            attrs={"placeholder": kwargs.get("label")},
        )
        autocomplete = kwargs.pop("autocomplete", None)
        if autocomplete is not None:
            kwargs["widget"].attrs["autocomplete"] = autocomplete
        super(PasswordField, self).__init__(*args, **kwargs)


class SetPasswordField(PasswordField):
    def __init__(self, *args, **kwargs):
        kwargs["autocomplete"] = "new-password"
        super(SetPasswordField, self).__init__(*args, **kwargs)
        self.user = None

    def clean(self, value):
        value = super(SetPasswordField, self).clean(value)
        value = get_adapter().clean_password(value, user=self.user)
        return value


class LoginForm(forms.Form):
    password = PasswordField(label=_("Password"), autocomplete="current-password")
    remember = forms.BooleanField(label=_("Remember Me"), required=False)

    user = None
    error_messages = {
        "account_inactive": _("This account is currently inactive."),
        "email_password_mismatch": _(
            "The email address and/or password you specified are not correct."
        ),
        "username_password_mismatch": _(
            "The username and/or password you specified are not correct."
        ),
    }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(LoginForm, self).__init__(*args, **kwargs)
        if app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.EMAIL:
            login_widget = forms.TextInput(
                attrs={
                    "type": "email",
                    "placeholder": _("Email address"),
                    "autocomplete": "email",
                }
            )
            login_field = forms.EmailField(label=_("Email"), widget=login_widget)
        elif app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.USERNAME:
            login_widget = forms.TextInput(
                attrs={"placeholder": _("Username"), "autocomplete": "username"}
            )
            login_field = forms.CharField(
                label=_("Username"),
                widget=login_widget,
                max_length=get_username_max_length(),
            )
        else:
            assert (
                app_settings.AUTHENTICATION_METHOD
                == AuthenticationMethod.USERNAME_EMAIL
            )
            login_widget = forms.TextInput(
                attrs={"placeholder": _("Username or email"), "autocomplete": "email"}
            )
            login_field = forms.CharField(
                label=pgettext("field label", "Login"), widget=login_widget
            )
        self.fields["login"] = login_field
        set_form_field_order(self, ["login", "password", "remember"])
        if app_settings.SESSION_REMEMBER is not None:
            del self.fields["remember"]
        try:
            reset_url = reverse("account_reset_password")
        except NoReverseMatch:
            pass
        else:
            forgot_txt = _("Forgot your password?")
            self.fields["password"].help_text = mark_safe(
                f'<a href="{reset_url}">{forgot_txt}</a>'
            )

    def user_credentials(self):
        """
        Provides the credentials required to authenticate the user for
        login.
        """
        credentials = {}
        login = self.cleaned_data["login"]
        if app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.EMAIL:
            credentials["email"] = login
        elif app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.USERNAME:
            credentials["username"] = login
        else:
            if self._is_login_email(login):
                credentials["email"] = login
            credentials["username"] = login
        credentials["password"] = self.cleaned_data["password"]
        return credentials

    def clean_login(self):
        login = self.cleaned_data["login"]
        return login.strip()

    def _is_login_email(self, login):
        try:
            validators.validate_email(login)
            ret = True
        except exceptions.ValidationError:
            ret = False
        return ret

    def clean(self):
        super(LoginForm, self).clean()
        if self._errors:
            return
        credentials = self.user_credentials()
        user = get_adapter(self.request).authenticate(self.request, **credentials)
        if user:
            self.user = user
        else:
            auth_method = app_settings.AUTHENTICATION_METHOD
            if auth_method == app_settings.AuthenticationMethod.USERNAME_EMAIL:
                login = self.cleaned_data["login"]
                if self._is_login_email(login):
                    auth_method = app_settings.AuthenticationMethod.EMAIL
                else:
                    auth_method = app_settings.AuthenticationMethod.USERNAME
            raise forms.ValidationError(
                self.error_messages["%s_password_mismatch" % auth_method]
            )
        return self.cleaned_data

    def login(self, request, redirect_url=None):
        email = self.user_credentials().get("email")
        ret = perform_login(
            request,
            self.user,
            email_verification=app_settings.EMAIL_VERIFICATION,
            redirect_url=redirect_url,
            email=email,
        )
        remember = app_settings.SESSION_REMEMBER
        if remember is None:
            remember = self.cleaned_data["remember"]
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
        fc_module, fc_classname = app_settings.SIGNUP_FORM_CLASS.rsplit(".", 1)
    except ValueError:
        raise exceptions.ImproperlyConfigured(
            "%s does not point to a form class" % app_settings.SIGNUP_FORM_CLASS
        )
    try:
        mod = import_module(fc_module)
    except ImportError as e:
        raise exceptions.ImproperlyConfigured(
            "Error importing form class %s:" ' "%s"' % (fc_module, e)
        )
    try:
        fc_class = getattr(mod, fc_classname)
    except AttributeError:
        raise exceptions.ImproperlyConfigured(
            'Module "%s" does not define a' ' "%s" class' % (fc_module, fc_classname)
        )
    if not hasattr(fc_class, "signup"):
        raise exceptions.ImproperlyConfigured(
            "The custom signup form must offer"
            " a `def signup(self, request, user)` method",
        )
    return fc_class


class BaseSignupForm(_base_signup_form_class()):
    username = forms.CharField(
        label=_("Username"),
        min_length=app_settings.USERNAME_MIN_LENGTH,
        widget=forms.TextInput(
            attrs={"placeholder": _("Username"), "autocomplete": "username"}
        ),
    )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "placeholder": _("Email address"),
                "autocomplete": "email",
            }
        )
    )

    def __init__(self, *args, **kwargs):
        email_required = kwargs.pop("email_required", app_settings.EMAIL_REQUIRED)
        self.username_required = kwargs.pop(
            "username_required", app_settings.USERNAME_REQUIRED
        )
        self.account_already_exists = False
        super(BaseSignupForm, self).__init__(*args, **kwargs)
        username_field = self.fields["username"]
        username_field.max_length = get_username_max_length()
        username_field.validators.append(
            validators.MaxLengthValidator(username_field.max_length)
        )
        username_field.widget.attrs["maxlength"] = str(username_field.max_length)

        default_field_order = [
            "email",
            "email2",  # ignored when not present
            "username",
            "password1",
            "password2",  # ignored when not present
        ]
        if app_settings.SIGNUP_EMAIL_ENTER_TWICE:
            self.fields["email2"] = forms.EmailField(
                label=_("Email (again)"),
                widget=forms.TextInput(
                    attrs={
                        "type": "email",
                        "placeholder": _("Email address confirmation"),
                    }
                ),
            )
        if email_required:
            self.fields["email"].label = gettext("Email")
            self.fields["email"].required = True
        else:
            self.fields["email"].label = gettext("Email (optional)")
            self.fields["email"].required = False
            self.fields["email"].widget.is_required = False
            if self.username_required:
                default_field_order = [
                    "username",
                    "email",
                    "email2",  # ignored when not present
                    "password1",
                    "password2",  # ignored when not present
                ]

        if not self.username_required:
            del self.fields["username"]

        set_form_field_order(
            self, getattr(self, "field_order", None) or default_field_order
        )

    def clean_username(self):
        value = self.cleaned_data["username"]
        value = get_adapter().clean_username(value)
        # Note regarding preventing enumeration: if the username is already
        # taken, but the email address is not, we would still leak information
        # if we were to send an email to that email address stating that the
        # username is already in use.
        return value

    def clean_email(self):
        value = self.cleaned_data["email"]
        value = get_adapter().clean_email(value)
        if value and app_settings.UNIQUE_EMAIL:
            value = self.validate_unique_email(value)
        return value

    def validate_unique_email(self, value):
        adapter = get_adapter()
        assessment = assess_unique_email(value)
        if assessment is True:
            # All good.
            pass
        elif assessment is False:
            # Fail right away.
            raise forms.ValidationError(adapter.error_messages["email_taken"])
        else:
            assert assessment is None
            self.account_already_exists = True
        return adapter.validate_unique_email(value)

    def clean(self):
        cleaned_data = super(BaseSignupForm, self).clean()
        if app_settings.SIGNUP_EMAIL_ENTER_TWICE:
            email = cleaned_data.get("email")
            email2 = cleaned_data.get("email2")
            if (email and email2) and email != email2:
                self.add_error("email2", _("You must type the same email each time."))
        return cleaned_data

    def custom_signup(self, request, user):
        self.signup(request, user)

    def try_save(self, request):
        """Try and save te user. This can fail in case of a conflict on the
        email address, in that case we will send an "account already exists"
        email and return a standard "email verification sent" response.
        """
        if self.account_already_exists:
            # Don't create a new account, only send an email informing the user
            # that (s)he already has one...
            email = self.cleaned_data["email"]
            adapter = get_adapter()
            adapter.send_account_already_exists_mail(email)
            user = None
            resp = adapter.respond_email_verification_sent(request, None)
        else:
            user = self.save(request)
            resp = None
        return user, resp


class SignupForm(BaseSignupForm):
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields["password1"] = PasswordField(
            label=_("Password"),
            autocomplete="new-password",
            help_text=password_validation.password_validators_help_text_html(),
        )
        if app_settings.SIGNUP_PASSWORD_ENTER_TWICE:
            self.fields["password2"] = PasswordField(
                label=_("Password (again)"), autocomplete="new-password"
            )

        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)

    def clean(self):
        super(SignupForm, self).clean()

        # `password` cannot be of type `SetPasswordField`, as we don't
        # have a `User` yet. So, let's populate a dummy user to be used
        # for password validation.
        User = get_user_model()
        dummy_user = User()
        user_username(dummy_user, self.cleaned_data.get("username"))
        user_email(dummy_user, self.cleaned_data.get("email"))
        password = self.cleaned_data.get("password1")
        if password:
            try:
                get_adapter().clean_password(password, user=dummy_user)
            except forms.ValidationError as e:
                self.add_error("password1", e)

        if (
            app_settings.SIGNUP_PASSWORD_ENTER_TWICE
            and "password1" in self.cleaned_data
            and "password2" in self.cleaned_data
        ):
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                self.add_error(
                    "password2",
                    _("You must type the same password each time."),
                )
        return self.cleaned_data

    def save(self, request):
        email = self.cleaned_data.get("email")
        if self.account_already_exists:
            raise ValueError(email)
        adapter = get_adapter()
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        # TODO: Move into adapter `save_user` ?
        setup_user_email(request, user, [EmailAddress(email=email)] if email else [])
        return user


class UserForm(forms.Form):
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)


class AddEmailForm(UserForm):
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.TextInput(
            attrs={"type": "email", "placeholder": _("Email address")}
        ),
    )

    def clean_email(self):
        from allauth.account import signals

        value = self.cleaned_data["email"]
        adapter = get_adapter()
        value = adapter.clean_email(value)
        errors = {
            "this_account": _(
                "This email address is already associated with this account."
            ),
            "max_email_addresses": _("You cannot add more than %d email addresses."),
        }
        users = filter_users_by_email(value)
        on_this_account = [u for u in users if u.pk == self.user.pk]
        on_diff_account = [u for u in users if u.pk != self.user.pk]

        if on_this_account:
            raise forms.ValidationError(errors["this_account"])
        if (
            on_diff_account
            and app_settings.PREVENT_ENUMERATION != "strict"
            and app_settings.UNIQUE_EMAIL
        ):
            raise forms.ValidationError(adapter.error_messages["email_taken"])
        if not EmailAddress.objects.can_add_email(self.user):
            raise forms.ValidationError(
                errors["max_email_addresses"] % app_settings.MAX_EMAIL_ADDRESSES
            )

        signals._add_email.send(
            sender=self.user.__class__,
            email=value,
            user=self.user,
        )
        return value

    def save(self, request):
        if app_settings.CHANGE_EMAIL:
            return EmailAddress.objects.add_new_email(
                request, self.user, self.cleaned_data["email"]
            )
        return EmailAddress.objects.add_email(
            request, self.user, self.cleaned_data["email"], confirm=True
        )


class ChangePasswordForm(PasswordVerificationMixin, UserForm):
    oldpassword = PasswordField(
        label=_("Current Password"), autocomplete="current-password"
    )
    password1 = SetPasswordField(
        label=_("New Password"),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = PasswordField(label=_("New Password (again)"))

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields["password1"].user = self.user

    def clean_oldpassword(self):
        if not self.user.check_password(self.cleaned_data.get("oldpassword")):
            raise forms.ValidationError(_("Please type your current password."))
        return self.cleaned_data["oldpassword"]

    def save(self):
        get_adapter().set_password(self.user, self.cleaned_data["password1"])


class SetPasswordForm(PasswordVerificationMixin, UserForm):
    password1 = SetPasswordField(
        label=_("Password"),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = PasswordField(label=_("Password (again)"))

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        self.fields["password1"].user = self.user

    def save(self):
        get_adapter().set_password(self.user, self.cleaned_data["password1"])


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "placeholder": _("Email address"),
                "autocomplete": "email",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        email = get_adapter().clean_email(email)
        self.users = filter_users_by_email(email, is_active=True, prefer_verified=True)
        if not self.users and not app_settings.PREVENT_ENUMERATION:
            raise forms.ValidationError(
                _("The email address is not assigned to any user account")
            )
        return self.cleaned_data["email"]

    def save(self, request, **kwargs):
        email = self.cleaned_data["email"]
        if not self.users:
            self._send_unknown_account_mail(request, email)
        else:
            self._send_password_reset_mail(request, email, self.users, **kwargs)
        return email

    def _send_unknown_account_mail(self, request, email):
        signup_url = build_absolute_uri(request, reverse("account_signup"))
        context = {
            "current_site": get_current_site(request),
            "email": email,
            "request": request,
            "signup_url": signup_url,
        }
        get_adapter().send_mail("account/email/unknown_account", email, context)

    def _send_password_reset_mail(self, request, email, users, **kwargs):
        token_generator = kwargs.get("token_generator", default_token_generator)

        for user in users:
            temp_key = token_generator.make_token(user)

            # save it to the password reset model
            # password_reset = PasswordReset(user=user, temp_key=temp_key)
            # password_reset.save()

            # send the password reset email
            uid = user_pk_to_url_str(user)
            path = reverse(
                "account_reset_password_from_key",
                kwargs=dict(uidb36=uid, key=temp_key),
            )
            url = build_absolute_uri(request, path)

            context = {
                "current_site": get_current_site(request),
                "user": user,
                "password_reset_url": url,
                "uid": uid,
                "key": temp_key,
                "request": request,
            }

            if app_settings.AUTHENTICATION_METHOD != AuthenticationMethod.EMAIL:
                context["username"] = user_username(user)
            get_adapter().send_mail("account/email/password_reset_key", email, context)


class ResetPasswordKeyForm(PasswordVerificationMixin, forms.Form):
    password1 = SetPasswordField(label=_("New Password"))
    password2 = PasswordField(label=_("New Password (again)"))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.temp_key = kwargs.pop("temp_key", None)
        super(ResetPasswordKeyForm, self).__init__(*args, **kwargs)
        self.fields["password1"].user = self.user

    def save(self):
        get_adapter().set_password(self.user, self.cleaned_data["password1"])


class UserTokenForm(forms.Form):
    uidb36 = forms.CharField()
    key = forms.CharField()

    reset_user = None
    token_generator = default_token_generator

    error_messages = {
        "token_invalid": _("The password reset token was invalid."),
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

        uidb36 = cleaned_data.get("uidb36", None)
        key = cleaned_data.get("key", None)

        if not key:
            raise forms.ValidationError(self.error_messages["token_invalid"])

        self.reset_user = self._get_user(uidb36)
        if self.reset_user is None or not self.token_generator.check_token(
            self.reset_user, key
        ):
            raise forms.ValidationError(self.error_messages["token_invalid"])

        return cleaned_data


class ReauthenticateForm(forms.Form):
    password = PasswordField(label=_("Password"), autocomplete="current-password")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.user.check_password(password):
            raise forms.ValidationError(
                get_adapter().error_messages["incorrect_password"]
            )
        return password
