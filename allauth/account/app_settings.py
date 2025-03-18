import warnings
from enum import Enum
from typing import FrozenSet, Set, Union


class AppSettings:
    class AuthenticationMethod(str, Enum):
        USERNAME = "username"
        EMAIL = "email"
        USERNAME_EMAIL = "username_email"

    class LoginMethod(str, Enum):
        USERNAME = "username"
        EMAIL = "email"
        PHONE = "phone"

    class EmailVerificationMethod(str, Enum):
        # After signing up, keep the user account inactive until the email
        # address is verified
        MANDATORY = "mandatory"
        # Allow login with unverified email (email verification is
        # still sent)
        OPTIONAL = "optional"
        # Don't send email verification mails during signup
        NONE = "none"

    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, dflt):
        from allauth.utils import get_setting

        return get_setting(self.prefix + name, dflt)

    @property
    def PREVENT_ENUMERATION(self):
        return self._setting("PREVENT_ENUMERATION", True)

    @property
    def DEFAULT_HTTP_PROTOCOL(self):
        return self._setting("DEFAULT_HTTP_PROTOCOL", "http").lower()

    @property
    def EMAIL_CONFIRMATION_EXPIRE_DAYS(self):
        """
        Determines the expiration date of email confirmation mails (#
        of days)
        """
        from django.conf import settings

        return self._setting(
            "EMAIL_CONFIRMATION_EXPIRE_DAYS",
            getattr(settings, "EMAIL_CONFIRMATION_DAYS", 3),
        )

    @property
    def EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL(self):
        """
        The URL to redirect to after a successful email confirmation, in
        case of an authenticated user
        """
        return self._setting("EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL", None)

    @property
    def EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL(self):
        """
        The URL to redirect to after a successful email confirmation, in
        case no user is logged in
        """
        from django.conf import settings

        return self._setting(
            "EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL", settings.LOGIN_URL
        )

    @property
    def EMAIL_REQUIRED(self):
        """
        The user is required to hand over an email address when signing up
        """
        warnings.warn(
            "app_settings.EMAIL_REQUIRED is deprecated, use: app_settings.SIGNUP_FIELDS['email']['required']",
            stacklevel=3,
        )
        email = self.SIGNUP_FIELDS.get("email")
        return email and email["required"]

    @property
    def EMAIL_VERIFICATION(self):
        """
        See email verification method
        """
        ret = self._setting("EMAIL_VERIFICATION", self.EmailVerificationMethod.OPTIONAL)
        # Deal with legacy (boolean based) setting
        if ret is True:
            ret = self.EmailVerificationMethod.MANDATORY
        elif ret is False:
            ret = self.EmailVerificationMethod.OPTIONAL
        return self.EmailVerificationMethod(ret)

    @property
    def EMAIL_VERIFICATION_BY_CODE_ENABLED(self):
        return self._setting("EMAIL_VERIFICATION_BY_CODE_ENABLED", False)

    @property
    def EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS(self):
        return self._setting("EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS", 3)

    @property
    def EMAIL_VERIFICATION_BY_CODE_TIMEOUT(self):
        return self._setting("EMAIL_VERIFICATION_BY_CODE_TIMEOUT", 15 * 60)

    @property
    def MAX_EMAIL_ADDRESSES(self):
        return self._setting("MAX_EMAIL_ADDRESSES", None)

    @property
    def CHANGE_EMAIL(self):
        return self._setting("CHANGE_EMAIL", False)

    @property
    def AUTHENTICATION_METHOD(self):
        warnings.warn(
            "app_settings.AUTHENTICATION_METHOD is deprecated, use: app_settings.LOGIN_METHODS",
            stacklevel=3,
        )
        methods = self.LOGIN_METHODS
        if self.LoginMethod.EMAIL in methods and self.LoginMethod.USERNAME in methods:
            return "username_email"
        elif self.LoginMethod.EMAIL in methods:
            return "email"
        elif self.LoginMethod.USERNAME in methods:
            return "username"
        else:
            raise NotADirectoryError

    @property
    def LOGIN_METHODS(self) -> FrozenSet[LoginMethod]:
        methods = self._setting("LOGIN_METHODS", None)
        if methods is None:
            auth_method = self._setting(
                "AUTHENTICATION_METHOD", self.AuthenticationMethod.USERNAME
            )
            if auth_method == self.AuthenticationMethod.USERNAME_EMAIL:
                methods = {self.LoginMethod.EMAIL, self.LoginMethod.USERNAME}
            else:
                methods = {self.LoginMethod(auth_method)}
        return frozenset([self.LoginMethod(m) for m in methods])

    @property
    def EMAIL_MAX_LENGTH(self):
        """
        Adjust max_length of email addresses
        """
        return self._setting("EMAIL_MAX_LENGTH", 254)

    @property
    def PHONE_VERIFICATION_ENABLED(self):
        return self._setting("PHONE_VERIFICATION_ENABLED", True)

    @property
    def PHONE_VERIFICATION_MAX_ATTEMPTS(self):
        return self._setting("PHONE_VERIFICATION_MAX_ATTEMPTS", 3)

    @property
    def PHONE_VERIFICATION_TIMEOUT(self):
        return self._setting("PHONE_VERIFICATION_TIMEOUT", 15 * 60)

    @property
    def UNIQUE_EMAIL(self):
        """
        Enforce uniqueness of email addresses
        """
        return self._setting("UNIQUE_EMAIL", True)

    @property
    def SIGNUP_EMAIL_ENTER_TWICE(self):
        """
        Signup email verification
        """
        warnings.warn(
            "app_settings.SIGNUP_EMAIL_ENTER_TWICE is deprecated, use: 'email2' in app_settings.SIGNUP_FIELDS",
            stacklevel=3,
        )
        return "email2" in self.SIGNUP_FIELDS

    @property
    def SIGNUP_PASSWORD_ENTER_TWICE(self):
        """
        Signup password verification
        """
        warnings.warn(
            "app_settings.SIGNUP_PASSWORD_ENTER_TWICE is deprecated, use: 'password2' in app_settings.SIGNUP_FIELDS",
            stacklevel=3,
        )
        return "password2" in self.SIGNUP_FIELDS

    @property
    def SIGNUP_REDIRECT_URL(self):
        from django.conf import settings

        return self._setting("SIGNUP_REDIRECT_URL", settings.LOGIN_REDIRECT_URL)

    @property
    def PASSWORD_MIN_LENGTH(self):
        """
        Minimum password Length
        """
        from django.conf import settings

        ret = None
        if not settings.AUTH_PASSWORD_VALIDATORS:
            ret = self._setting("PASSWORD_MIN_LENGTH", 6)
        return ret

    @property
    def RATE_LIMITS(self):
        rls = self._setting("RATE_LIMITS", {})
        if rls is False:
            return {}
        attempts_amount = self._setting("LOGIN_ATTEMPTS_LIMIT", 5)
        attempts_timeout = self._setting("LOGIN_ATTEMPTS_TIMEOUT", 60 * 5)
        login_failed_rl = None
        if attempts_amount and attempts_timeout:
            login_failed_rl = f"10/m/ip,{attempts_amount}/{attempts_timeout}s/key"

        if self.EMAIL_VERIFICATION_BY_CODE_ENABLED:
            confirm_email_rl = "1/10s/key"
        else:
            cooldown = self._setting("EMAIL_CONFIRMATION_COOLDOWN", 3 * 60)
            confirm_email_rl = None
            if cooldown:
                confirm_email_rl = f"1/{cooldown}s/key"
        ret = {
            # Change password view (for users already logged in)
            "change_password": "5/m/user",
            # Change phone number
            "change_phone": "1/m/user",
            # Email management (e.g. add, remove, change primary)
            "manage_email": "10/m/user",
            # Request a password reset, global rate limit per IP
            "reset_password": "20/m/ip,5/m/key",
            # Reauthentication for users already logged in
            "reauthenticate": "10/m/user",
            # Password reset (the view the password reset email links to).
            "reset_password_from_key": "20/m/ip",
            # Signups.
            "signup": "20/m/ip",
            # Logins.
            "login": "30/m/ip",
            # Request a login code: key is the email.
            "request_login_code": "20/m/ip,3/m/key",
            # Logins.
            "login_failed": login_failed_rl,
            # Confirm email
            "confirm_email": confirm_email_rl,
        }
        ret.update(rls)
        return ret

    @property
    def EMAIL_SUBJECT_PREFIX(self):
        """
        Subject-line prefix to use for email messages sent
        """
        return self._setting("EMAIL_SUBJECT_PREFIX", None)

    @property
    def SIGNUP_FORM_CLASS(self):
        """
        Signup form
        """
        return self._setting("SIGNUP_FORM_CLASS", None)

    @property
    def SIGNUP_FORM_HONEYPOT_FIELD(self):
        """
        Honeypot field name. Empty string or ``None`` will disable honeypot behavior.
        """
        return self._setting("SIGNUP_FORM_HONEYPOT_FIELD", None)

    @property
    def SIGNUP_FIELDS(self) -> dict:
        fields = self._setting("SIGNUP_FIELDS", None)
        if not fields:
            fields = []
            username = self._setting("USERNAME_REQUIRED", True)
            email = self._setting("EMAIL_REQUIRED", False)
            email2 = self._setting("SIGNUP_EMAIL_ENTER_TWICE", False)
            password2 = self._setting(
                "SIGNUP_PASSWORD_ENTER_TWICE",
                self._setting("SIGNUP_PASSWORD_VERIFICATION", True),
            )
            if email:
                fields.append("email*")
            else:
                fields.append("email")
            if email2:
                fields.append("email2*" if email else "email2")
            if username:
                fields.append("username*")
            fields.append("password1*")
            if password2:
                fields.append("password2*")
        ret = {}
        for field in fields:
            f, req, _ = field.partition("*")
            ret[f] = {"required": bool(req)}
        return ret

    @property
    def USERNAME_REQUIRED(self):
        """
        The user is required to enter a username when signing up
        """
        warnings.warn(
            "app_settings.USERNAME_REQUIRED is deprecated, use: app_settings.SIGNUP_FIELDS['username']['required']",
            stacklevel=3,
        )
        username = self.SIGNUP_FIELDS.get("username")
        return username and username["required"]

    @property
    def USERNAME_MIN_LENGTH(self):
        """
        Minimum username Length
        """
        return self._setting("USERNAME_MIN_LENGTH", 1)

    @property
    def USERNAME_BLACKLIST(self):
        """
        List of usernames that are not allowed
        """
        return self._setting("USERNAME_BLACKLIST", [])

    @property
    def PASSWORD_INPUT_RENDER_VALUE(self):
        """
        render_value parameter as passed to PasswordInput fields
        """
        return self._setting("PASSWORD_INPUT_RENDER_VALUE", False)

    @property
    def ADAPTER(self):
        return self._setting("ADAPTER", "allauth.account.adapter.DefaultAccountAdapter")

    @property
    def CONFIRM_EMAIL_ON_GET(self):
        return self._setting("CONFIRM_EMAIL_ON_GET", False)

    @property
    def AUTHENTICATED_LOGIN_REDIRECTS(self):
        return self._setting("AUTHENTICATED_LOGIN_REDIRECTS", True)

    @property
    def LOGIN_ON_EMAIL_CONFIRMATION(self):
        """
        Automatically log the user in once they confirmed their email address
        """
        return self._setting("LOGIN_ON_EMAIL_CONFIRMATION", False)

    @property
    def LOGIN_ON_PASSWORD_RESET(self):
        """
        Automatically log the user in immediately after resetting
        their password.
        """
        return self._setting("LOGIN_ON_PASSWORD_RESET", False)

    @property
    def LOGOUT_REDIRECT_URL(self):
        from django.conf import settings

        return self._setting("LOGOUT_REDIRECT_URL", settings.LOGOUT_REDIRECT_URL or "/")

    @property
    def LOGOUT_ON_GET(self):
        return self._setting("LOGOUT_ON_GET", False)

    @property
    def LOGOUT_ON_PASSWORD_CHANGE(self):
        return self._setting("LOGOUT_ON_PASSWORD_CHANGE", False)

    @property
    def USER_MODEL_USERNAME_FIELD(self):
        return self._setting("USER_MODEL_USERNAME_FIELD", "username")

    @property
    def USER_MODEL_EMAIL_FIELD(self):
        return self._setting("USER_MODEL_EMAIL_FIELD", "email")

    @property
    def SESSION_COOKIE_AGE(self):
        """
        Deprecated -- use Django's settings.SESSION_COOKIE_AGE instead
        """
        from django.conf import settings

        return self._setting("SESSION_COOKIE_AGE", settings.SESSION_COOKIE_AGE)

    @property
    def SESSION_REMEMBER(self):
        """
        Controls the life time of the session. Set to `None` to ask the user
        ("Remember me?"), `False` to not remember, and `True` to always
        remember.
        """
        return self._setting("SESSION_REMEMBER", None)

    @property
    def TEMPLATE_EXTENSION(self):
        """
        A string defining the template extension to use, defaults to `html`.
        """
        return self._setting("TEMPLATE_EXTENSION", "html")

    @property
    def FORMS(self):
        return self._setting("FORMS", {})

    @property
    def EMAIL_CONFIRMATION_HMAC(self):
        return self._setting("EMAIL_CONFIRMATION_HMAC", True)

    @property
    def SALT(self):
        return self._setting("SALT", "account")

    @property
    def PRESERVE_USERNAME_CASING(self):
        return self._setting("PRESERVE_USERNAME_CASING", True)

    @property
    def USERNAME_VALIDATORS(self):
        from django.contrib.auth import get_user_model
        from django.core.exceptions import ImproperlyConfigured

        from allauth.utils import import_attribute

        path = self._setting("USERNAME_VALIDATORS", None)
        if path:
            ret = import_attribute(path)
            if not isinstance(ret, list):
                raise ImproperlyConfigured(
                    "ACCOUNT_USERNAME_VALIDATORS is expected to be a list"
                )
        else:
            if self.USER_MODEL_USERNAME_FIELD is not None:
                ret = (
                    get_user_model()
                    ._meta.get_field(self.USER_MODEL_USERNAME_FIELD)
                    .validators
                )
            else:
                ret = []
        return ret

    @property
    def PASSWORD_RESET_BY_CODE_ENABLED(self):
        return self._setting("PASSWORD_RESET_BY_CODE_ENABLED", False)

    @property
    def PASSWORD_RESET_BY_CODE_MAX_ATTEMPTS(self):
        return self._setting("PASSWORD_RESET_BY_CODE_MAX_ATTEMPTS", 3)

    @property
    def PASSWORD_RESET_BY_CODE_TIMEOUT(self):
        return self._setting("PASSWORD_RESET_BY_CODE_TIMEOUT", 3 * 60)

    @property
    def PASSWORD_RESET_TOKEN_GENERATOR(self):
        from allauth.account.forms import EmailAwarePasswordResetTokenGenerator
        from allauth.utils import import_attribute

        token_generator_path = self._setting("PASSWORD_RESET_TOKEN_GENERATOR", None)
        if token_generator_path is not None:
            token_generator = import_attribute(token_generator_path)
        else:
            token_generator = EmailAwarePasswordResetTokenGenerator
        return token_generator

    @property
    def EMAIL_UNKNOWN_ACCOUNTS(self):
        return self._setting("EMAIL_UNKNOWN_ACCOUNTS", True)

    @property
    def REAUTHENTICATION_TIMEOUT(self):
        return self._setting("REAUTHENTICATION_TIMEOUT", 300)

    @property
    def EMAIL_NOTIFICATIONS(self):
        return self._setting("EMAIL_NOTIFICATIONS", False)

    @property
    def REAUTHENTICATION_REQUIRED(self):
        return self._setting("REAUTHENTICATION_REQUIRED", False)

    @property
    def LOGIN_BY_CODE_ENABLED(self):
        return self._setting("LOGIN_BY_CODE_ENABLED", False)

    @property
    def LOGIN_BY_CODE_MAX_ATTEMPTS(self):
        return self._setting("LOGIN_BY_CODE_MAX_ATTEMPTS", 3)

    @property
    def LOGIN_BY_CODE_TIMEOUT(self):
        return self._setting("LOGIN_BY_CODE_TIMEOUT", 3 * 60)

    @property
    def LOGIN_TIMEOUT(self):
        """
        The maximum allowed time (in seconds) for a login to go through the
        various login stages. This limits, for example, the time span that the
        2FA stage remains available.
        """
        return self._setting("LOGIN_TIMEOUT", 15 * 60)

    @property
    def LOGIN_BY_CODE_REQUIRED(self) -> Union[bool, Set[str]]:
        """
        When enabled (in case of ``True``), every user logging in is
        required to input a login confirmation code sent by email.
        Alternatively, you can specify a set of authentication methods
        (``"password"``, ``"mfa"``, or ``"socialaccount"``) for which login
        codes are required.
        """
        value = self._setting("LOGIN_BY_CODE_REQUIRED", False)
        if isinstance(value, bool):
            return value
        return set(value)


_app_settings = AppSettings("ACCOUNT_")


def __getattr__(name):
    # See https://peps.python.org/pep-0562/
    return getattr(_app_settings, name)
