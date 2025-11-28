from typing import Optional

from django import forms
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model, password_validation
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import exceptions, validators
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _, pgettext

from allauth.account.app_settings import LoginMethod
from allauth.account.fields import EmailField, PasswordField, SetPasswordField
from allauth.account.internal import flows
from allauth.account.internal.flows.manage_email import (
    email_already_exists,
    sync_user_email_address,
)
from allauth.account.internal.flows.phone_verification import phone_already_exists
from allauth.account.internal.flows.signup import base_signup_form_class
from allauth.core import context, ratelimit
from allauth.core.internal.cryptokit import compare_user_code
from allauth.core.internal.httpkit import headed_redirect_response
from allauth.utils import get_username_max_length, set_form_field_order

from . import app_settings
from .adapter import get_adapter
from .models import EmailAddress, Login
from .utils import (
    filter_users_by_email,
    setup_user_email,
    url_str_to_user_pk,
    user_email,
    user_username,
)


class EmailAwarePasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        ret = super()._make_hash_value(user, timestamp)
        sync_user_email_address(user)
        email = user_email(user)
        emails = set([email] if email else [])
        emails.update(
            EmailAddress.objects.filter(user=user).values_list("email", flat=True)
        )
        ret += "|".join(sorted(emails))
        return ret


default_token_generator = app_settings.PASSWORD_RESET_TOKEN_GENERATOR()


class PasswordVerificationMixin:
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if (password1 and password2) and password1 != password2:
            self.add_error("password2", _("You must type the same password each time."))
        return cleaned_data


class LoginForm(forms.Form):
    password = PasswordField(label=_("Password"), autocomplete="current-password")
    remember = forms.BooleanField(label=_("Remember Me"), required=False)

    user = None

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        adapter = get_adapter()
        if app_settings.LOGIN_METHODS == {LoginMethod.EMAIL}:
            login_field = EmailField()
        elif app_settings.LOGIN_METHODS == {LoginMethod.USERNAME}:
            login_widget = forms.TextInput(
                attrs={"placeholder": _("Username"), "autocomplete": "username"}
            )
            login_field = forms.CharField(
                label=_("Username"),
                widget=login_widget,
                max_length=get_username_max_length(),
            )
        elif app_settings.LOGIN_METHODS == {LoginMethod.PHONE}:
            login_field = adapter.phone_form_field(required=True)
        else:
            login_widget = forms.TextInput(
                attrs={
                    "placeholder": self._get_login_field_placeholder(),
                    "autocomplete": "email",
                }
            )
            login_field = forms.CharField(
                label=pgettext("field label", "Login"), widget=login_widget
            )
        self.fields["login"] = login_field
        set_form_field_order(self, ["login", "password", "remember"])
        if app_settings.SESSION_REMEMBER is not None:
            del self.fields["remember"]
        self._setup_password_field()

    def _get_login_field_placeholder(self):
        methods = app_settings.LOGIN_METHODS
        assert len(methods) > 1  # nosec
        assert methods.issubset(
            {
                LoginMethod.USERNAME,
                LoginMethod.EMAIL,
                LoginMethod.PHONE,
            }
        )  # nosec
        if len(methods) == 3:
            placeholder = _("Username, email or phone")
        elif methods == {LoginMethod.USERNAME, LoginMethod.EMAIL}:
            placeholder = _("Username or email")
        elif methods == {LoginMethod.USERNAME, LoginMethod.PHONE}:
            placeholder = _("Username or phone")
        elif methods == {LoginMethod.EMAIL, LoginMethod.PHONE}:
            placeholder = _("Email or phone")
        else:
            raise ValueError(methods)
        return placeholder

    def _setup_password_field(self):
        password_field = app_settings.SIGNUP_FIELDS.get("password1")
        if not password_field:
            del self.fields["password"]
            return
        try:
            self.fields["password"].help_text = render_to_string(
                f"account/password_reset_help_text.{app_settings.TEMPLATE_EXTENSION}"
            )
            return
        except TemplateDoesNotExist:
            pass

        try:
            reset_url = reverse("account_reset_password")
        except NoReverseMatch:
            pass
        else:
            forgot_txt = _("Forgot your password?")
            self.fields["password"].help_text = mark_safe(
                f'<a href="{reset_url}">{forgot_txt}</a>'
            )  # nosec

    def user_credentials(self) -> dict:
        """
        Provides the credentials required to authenticate the user for
        login.
        """
        login = self.cleaned_data["login"]
        method = flows.login.derive_login_method(login)
        credentials = {}
        credentials[method] = login

        # There are projects using usernames that look like email addresses,
        # yet, really are usernames. So, if username is a login method, always
        # give that a shot.
        if (
            LoginMethod.USERNAME in app_settings.LOGIN_METHODS
            and method != LoginMethod.USERNAME
        ):
            credentials[LoginMethod.USERNAME] = login

        password = self.cleaned_data.get("password")
        if password:
            credentials["password"] = password
        return credentials

    def clean_login(self):
        login = self.cleaned_data["login"]
        return login.strip()

    def clean(self):
        super().clean()
        if self._errors:
            return
        credentials = self.user_credentials()
        if "password" in credentials:
            return self._clean_with_password(credentials)
        return self._clean_without_password(
            credentials.get("email"), credentials.get("phone")
        )

    def _clean_without_password(self, email: Optional[str], phone: Optional[str]):
        """
        If we don't have a password field, we need to replicate the request-login-code
        behavior.
        """
        data = {}
        if email:
            data["email"] = email
        if phone:
            data["phone"] = phone
        if not data:
            self.add_error("login", get_adapter().validation_error("invalid_login"))
        else:
            form = RequestLoginCodeForm(data)
            if not form.is_valid():
                for field in ["phone", "email"]:
                    errors = form.errors.get(field) or []  # type: ignore
                    for error in errors:
                        self.add_error("login", error)
            else:
                self.user = form._user  # type: ignore
        return self.cleaned_data

    def _clean_with_password(self, credentials: dict):
        adapter = get_adapter(self.request)
        user = adapter.authenticate(self.request, **credentials)
        if user:
            login = Login(user=user, email=credentials.get("email"))
            if flows.login.is_login_rate_limited(context.request, login):
                raise adapter.validation_error("too_many_login_attempts")
            self._login = login
            self.user = user  # type: ignore
        else:
            login_method = flows.login.derive_login_method(
                login=self.cleaned_data["login"]
            )
            raise adapter.validation_error(f"{login_method.value}_password_mismatch")
        return self.cleaned_data

    def login(self, request, redirect_url=None):
        credentials = self.user_credentials()
        if "password" in credentials:
            return self._login_with_password(request, redirect_url, credentials)
        return self._login_by_code(request, redirect_url, credentials)

    def _login_by_code(self, request, redirect_url, credentials):
        user = getattr(self, "user", None)
        phone = credentials.get("phone")
        email = credentials.get("email")
        flows.login_by_code.LoginCodeVerificationProcess.initiate(
            request=request,
            user=user,
            phone=phone,
            email=email,
        )
        query = None
        if redirect_url:
            query = {}
            query[REDIRECT_FIELD_NAME] = redirect_url
        return headed_redirect_response("account_confirm_login_code", query=query)

    def _login_with_password(self, request, redirect_url, credentials):
        login = self._login
        login.redirect_url = redirect_url
        ret = flows.login.perform_password_login(request, credentials, login)
        remember = app_settings.SESSION_REMEMBER
        if remember is None:
            remember = self.cleaned_data["remember"]
        if remember:
            request.session.set_expiry(app_settings.SESSION_COOKIE_AGE)
        else:
            request.session.set_expiry(0)
        return ret


class BaseSignupForm(base_signup_form_class()):  # type: ignore[misc]
    username = forms.CharField(
        label=_("Username"),
        min_length=app_settings.USERNAME_MIN_LENGTH,
        widget=forms.TextInput(
            attrs={"placeholder": _("Username"), "autocomplete": "username"}
        ),
    )
    email = EmailField()

    def __init__(self, *args, **kwargs):
        self._signup_fields = self._get_signup_fields(kwargs)
        self.account_already_exists = False
        super().__init__(*args, **kwargs)
        username_field = self.fields["username"]
        username_field.max_length = get_username_max_length()
        username_field.validators.append(
            validators.MaxLengthValidator(username_field.max_length)
        )
        username_field.widget.attrs["maxlength"] = str(username_field.max_length)

        email2 = self._signup_fields.get("email2")
        if email2:
            self.fields["email2"] = EmailField(
                label=_("Email (again)"),
                required=email2["required"],
                widget=forms.TextInput(
                    attrs={
                        "type": "email",
                        "placeholder": _("Email address confirmation"),
                    }
                ),
            )
        email = self._signup_fields.get("email")
        if email:
            if email["required"]:
                self.fields["email"].label = gettext("Email")
                self.fields["email"].required = True
            else:
                self.fields["email"].label = gettext("Email (optional)")
                self.fields["email"].required = False
                self.fields["email"].widget.is_required = False
        else:
            del self.fields["email"]

        username = self._signup_fields.get("username")
        if username:
            if username["required"]:
                self.fields["username"].label = gettext("Username")
                self.fields["username"].required = True
            else:
                self.fields["username"].label = gettext("Username (optional)")
                self.fields["username"].required = False
                self.fields["username"].widget.is_required = False
        else:
            del self.fields["username"]

        phone = self._signup_fields.get("phone")
        self._has_phone_field = bool(phone)
        if phone:
            adapter = get_adapter()
            self.fields["phone"] = adapter.phone_form_field(
                label=_("Phone"), required=phone["required"]
            )

        default_field_order = list(self._signup_fields.keys())
        set_form_field_order(
            self, getattr(self, "field_order", None) or default_field_order
        )

    def _get_signup_fields(self, kwargs):
        signup_fields = app_settings.SIGNUP_FIELDS
        if "email_required" in kwargs:
            email = signup_fields.get("email")
            if not email:
                raise exceptions.ImproperlyConfigured(
                    "email required but not listed as a field"
                )
            email["required"] = kwargs.pop("email_required")
            email2 = signup_fields.get("email2")
            if email2:
                email2["required"] = email["required"]
        if "username_required" in kwargs:
            username = signup_fields.get("username")
            if not username:
                raise exceptions.ImproperlyConfigured(
                    "username required but not listed as a field"
                )
            username["required"] = kwargs.pop("username_required")
        return signup_fields

    def clean_username(self):
        value = self.cleaned_data["username"]
        if not value and not self._signup_fields["username"]["required"]:
            return value
        value = get_adapter().clean_username(value)
        # Note regarding preventing enumeration: if the username is already
        # taken, but the email address is not, we would still leak information
        # if we were to send an email to that email address stating that the
        # username is already in use.
        return value

    def clean_email(self):
        value = self.cleaned_data["email"].lower()
        value = get_adapter().clean_email(value)
        if value:
            value = self.validate_unique_email(value)
        return value

    def clean_email2(self):
        value = self.cleaned_data["email2"].lower()
        return value

    def validate_unique_email(self, value) -> str:
        email, self.account_already_exists = flows.manage_email.email_already_exists(
            value
        )
        return email

    def clean(self):
        cleaned_data = super().clean()
        if "email2" in self._signup_fields:
            email = cleaned_data.get("email")
            email2 = cleaned_data.get("email2")
            if (email and email2) and email != email2:
                self.add_error("email2", _("You must type the same email each time."))

        if "phone" in self._signup_fields:
            self._clean_phone()
        return cleaned_data

    def _clean_phone(self):
        """Intentionally NOT `clean_phone()`:
        - phone field is optional (depending on ACCOUNT_SIGNUP_FIELDS)
        - we don't want to have clean_phone() mistakenly called when a project
          is using a custom signup form with their own `phone` field.
        """
        adapter = get_adapter()
        if phone := self.cleaned_data.get("phone"):
            user = adapter.get_user_by_phone(phone)
            if user:
                if not app_settings.PREVENT_ENUMERATION:
                    self.add_error("phone", adapter.error_messages["phone_taken"])
                else:
                    self.account_already_exists = True

    def custom_signup(self, request, user):
        self.signup(request, user)

    def try_save(self, request):
        """Try and save the user. This can fail in case of a conflict on the
        email address, in that case we will send an "account already exists"
        email and return a standard "email verification sent" response.
        """
        if self.account_already_exists:
            # Don't create a new account, only send an email informing the user
            # that (s)he already has one...
            email = self.cleaned_data.get("email")
            phone = None
            if "phone" in self._signup_fields:
                phone = self.cleaned_data.get("phone")
            resp = flows.signup.prevent_enumeration(request, email=email, phone=phone)
            user = None
        else:
            user = self.save(request)
            resp = None
        return user, resp

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


class SignupForm(BaseSignupForm):
    def __init__(self, *args, **kwargs):
        self.by_passkey = kwargs.pop("by_passkey", False)
        super().__init__(*args, **kwargs)
        password1_field = self._signup_fields.get("password1")
        if not self.by_passkey and password1_field:
            self.fields["password1"] = PasswordField(
                label=_("Password"),
                autocomplete="new-password",
                help_text=password_validation.password_validators_help_text_html(),
                required=password1_field["required"],
            )
            if "password2" in self._signup_fields:
                self.fields["password2"] = PasswordField(
                    label=_("Password (again)"),
                    autocomplete="new-password",
                    required=password1_field["required"],
                )

        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)

        honeypot_field_name = app_settings.SIGNUP_FORM_HONEYPOT_FIELD
        if honeypot_field_name:
            self.fields[honeypot_field_name] = forms.CharField(
                required=False,
                label="",
                widget=forms.TextInput(
                    attrs={
                        "style": "position: absolute; right: -99999px;",
                        "tabindex": "-1",
                        "autocomplete": "nope",
                    }
                ),
            )

    def try_save(self, request):
        """
        override of parent class method that adds additional catching
        of a potential bot filling out the honeypot field and returns a
        'fake' email verification response if honeypot was filled out
        """
        honeypot_field_name = app_settings.SIGNUP_FORM_HONEYPOT_FIELD
        if honeypot_field_name:
            if self.cleaned_data[honeypot_field_name]:
                user = None
                adapter = get_adapter()
                # honeypot fields work best when you do not report to the bot
                # that anything went wrong. So we return a fake email verification
                # sent response but without creating a user
                resp = adapter.respond_email_verification_sent(request, None)
                return user, resp

        return super().try_save(request)

    def clean(self):
        super().clean()

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
            "password2" in self._signup_fields
            and "password1" in self.cleaned_data
            and "password2" in self.cleaned_data
        ):
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                self.add_error(
                    "password2",
                    _("You must type the same password each time."),
                )
        return self.cleaned_data


class UserForm(forms.Form):
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)


class AddEmailForm(UserForm):
    email = EmailField(required=True)

    def clean_email(self):
        from allauth.account import signals

        value = self.cleaned_data["email"].lower()
        adapter = get_adapter()
        value = adapter.clean_email(value)
        users = filter_users_by_email(value)
        on_this_account = [u for u in users if u.pk == self.user.pk]
        on_diff_account = [u for u in users if u.pk != self.user.pk]

        if on_this_account:
            raise adapter.validation_error("duplicate_email")
        if (
            # Email is taken by a different account...
            on_diff_account
            # We care about not having duplicate emails
            and app_settings.UNIQUE_EMAIL
            # Enumeration prevention is turned off.
            and (not app_settings.PREVENT_ENUMERATION)
        ):
            raise adapter.validation_error("email_taken")
        if not EmailAddress.objects.can_add_email(self.user):
            raise adapter.validation_error(
                "max_email_addresses", app_settings.MAX_EMAIL_ADDRESSES
            )

        signals._add_email.send(
            sender=self.user.__class__,
            email=value,
            user=self.user,
        )
        return value

    def save(self, request):
        if app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
            email_address = EmailAddress(
                user=self.user, email=self.cleaned_data["email"]
            )
            flows.email_verification.send_verification_email_to_address(
                request, email_address
            )
            return email_address
        elif app_settings.CHANGE_EMAIL:
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
    password1 = SetPasswordField(label=_("New Password"))
    password2 = PasswordField(label=_("New Password (again)"))

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields["password1"].user = self.user

    def clean_oldpassword(self):
        if not self.user.check_password(self.cleaned_data.get("oldpassword")):
            raise get_adapter().validation_error("enter_current_password")
        return self.cleaned_data["oldpassword"]

    def save(self):
        flows.password_change.change_password(self.user, self.cleaned_data["password1"])


class SetPasswordForm(PasswordVerificationMixin, UserForm):
    password1 = SetPasswordField(label=_("Password"))
    password2 = PasswordField(label=_("Password (again)"))

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        self.fields["password1"].user = self.user

    def save(self):
        flows.password_change.change_password(self.user, self.cleaned_data["password1"])


class ResetPasswordForm(forms.Form):
    email = EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        email = get_adapter().clean_email(email)
        self.users = filter_users_by_email(email, is_active=True, prefer_verified=True)
        if not self.users and not app_settings.PREVENT_ENUMERATION:
            raise get_adapter().validation_error("unknown_email")
        return self.cleaned_data["email"]

    def save(self, request, **kwargs) -> str:
        email = self.cleaned_data["email"]
        if app_settings.PASSWORD_RESET_BY_CODE_ENABLED:
            flows.password_reset_by_code.PasswordResetVerificationProcess.initiate(
                request=request,
                user=(self.users[0] if self.users else None),
                email=email,
            )
        else:
            token_generator = kwargs.get("token_generator", default_token_generator)
            flows.password_reset.request_password_reset(
                request, email, self.users, token_generator
            )
        return email


class ResetPasswordKeyForm(PasswordVerificationMixin, forms.Form):
    password1 = SetPasswordField(label=_("New Password"))
    password2 = PasswordField(label=_("New Password (again)"))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.temp_key = kwargs.pop("temp_key", None)
        super().__init__(*args, **kwargs)
        self.fields["password1"].user = self.user

    def save(self):
        flows.password_reset.reset_password(self.user, self.cleaned_data["password1"])


class UserTokenForm(forms.Form):
    uidb36 = forms.CharField()
    key = forms.CharField()

    reset_user = None
    token_generator = default_token_generator

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
        adapter = get_adapter()
        if not key:
            raise adapter.validation_error("invalid_password_reset")

        self.reset_user = self._get_user(uidb36)
        if self.reset_user is None or not self.token_generator.check_token(
            self.reset_user, key
        ):
            raise adapter.validation_error("invalid_password_reset")

        return cleaned_data


class ReauthenticateForm(forms.Form):
    password = PasswordField(label=_("Password"), autocomplete="current-password")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not get_adapter().reauthenticate(self.user, password):
            raise get_adapter().validation_error("incorrect_password")
        return password


class RequestLoginCodeForm(forms.Form):
    email = EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._has_email = LoginMethod.EMAIL in app_settings.LOGIN_METHODS
        self._has_phone = LoginMethod.PHONE in app_settings.LOGIN_METHODS
        if self._has_phone:
            adapter = get_adapter()
            self.fields["phone"] = adapter.phone_form_field(
                required=not self._has_email
            )
            self.fields["email"].required = False
        # Inconsistent, but kept for backwards compatibility: even if email is not a login
        # method the email field is added. May be used when login is by username.
        if self._has_phone and not self._has_email:
            self.fields.pop("email")

    def clean(self):
        cleaned_data = super().clean()
        adapter = get_adapter()
        phone = cleaned_data.get("phone")
        email = cleaned_data.get("email")
        if email and phone:
            raise adapter.validation_error("select_only_one")
        return cleaned_data

    def clean_phone(self):
        adapter = get_adapter()
        phone = self.cleaned_data["phone"]
        if phone:
            self._user = adapter.get_user_by_phone(phone)
            if not self._user and not app_settings.PREVENT_ENUMERATION:
                raise adapter.validation_error("unknown_phone")
            if not ratelimit.consume(
                context.request, action="request_login_code", key=phone.lower()
            ):
                raise adapter.validation_error("too_many_login_attempts")
        return phone

    def clean_email(self):
        adapter = get_adapter()
        email = self.cleaned_data["email"]
        if email:
            users = filter_users_by_email(email, is_active=True, prefer_verified=True)
            if not app_settings.PREVENT_ENUMERATION:
                if not users:
                    raise adapter.validation_error("unknown_email")
            if not ratelimit.consume(
                context.request, action="request_login_code", key=email.lower()
            ):
                raise adapter.validation_error("too_many_login_attempts")
            self._user = users[0] if users else None
        return email


class BaseConfirmCodeForm(forms.Form):
    code = forms.CharField(
        label=_("Code"),
        widget=forms.TextInput(
            attrs={"placeholder": _("Code"), "autocomplete": "one-time-code"},
        ),
    )

    def __init__(self, *args, **kwargs):
        self.code = kwargs.pop("code", None)
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if not compare_user_code(actual=code, expected=self.code):
            raise get_adapter().validation_error("incorrect_code")
        return code


class ConfirmLoginCodeForm(BaseConfirmCodeForm):
    pass


class ConfirmEmailVerificationCodeForm(BaseConfirmCodeForm):
    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop("user", None)
        self.email = kwargs.pop("email", None)
        super().__init__(*args, **kwargs)

    def clean_code(self) -> str:
        code = super().clean_code()
        if code:
            # We have a valid code. But, can we actually perform the change?
            email_already_exists(user=self.user, email=self.email, always_raise=True)
        return code


class ConfirmPasswordResetCodeForm(BaseConfirmCodeForm):
    pass


class VerifyPhoneForm(BaseConfirmCodeForm):
    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop("user", None)
        self.phone = kwargs.pop("phone", None)
        super().__init__(*args, **kwargs)

    def clean_code(self) -> str:
        code = super().clean_code()
        if code:
            # We have a valid code. But, can we actually perform the change?
            phone_already_exists(self.user, self.phone, always_raise=True)
        return code


class ChangePhoneForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.phone = kwargs.pop("phone", None)
        super().__init__(*args, **kwargs)
        adapter = get_adapter()
        self.fields["phone"] = adapter.phone_form_field(required=True)

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        adapter = get_adapter()
        if phone == self.phone:
            raise adapter.validation_error("same_as_current")
        self.account_already_exists = phone_already_exists(self.user, phone)
        return phone


class ChangeEmailForm(forms.Form):
    email = EmailField(required=True)

    def __init__(self, *args, **kwargs):
        self.email = kwargs.pop("email", None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email == self.email:
            raise get_adapter().validation_error("same_as_current")
        email, self.account_already_exists = email_already_exists(email)
        return email
