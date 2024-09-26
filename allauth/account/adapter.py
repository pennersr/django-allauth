import html
import json
import string
import warnings
from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_backends,
    get_user_model,
    login as django_login,
    logout as django_logout,
)
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    validate_password,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import FieldDoesNotExist
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from allauth import app_settings as allauth_app_settings
from allauth.account import app_settings, signals
from allauth.core import context, ratelimit
from allauth.core.internal.adapter import BaseAdapter
from allauth.core.internal.httpkit import headed_redirect_response
from allauth.utils import generate_unique_username, import_attribute


class DefaultAccountAdapter(BaseAdapter):
    """The adapter class allows you to override various functionality of the
    ``allauth.account`` app.  To do so, point ``settings.ACCOUNT_ADAPTER`` to
    your own class that derives from ``DefaultAccountAdapter`` and override the
    behavior by altering the implementation of the methods according to your own
    needs.
    """

    error_messages = {
        "account_inactive": _("This account is currently inactive."),
        "cannot_remove_primary_email": _(
            "You cannot remove your primary email address."
        ),
        "duplicate_email": _(
            "This email address is already associated with this account."
        ),
        "email_password_mismatch": _(
            "The email address and/or password you specified are not correct."
        ),
        "email_taken": _("A user is already registered with this email address."),
        "enter_current_password": _("Please type your current password."),
        "incorrect_code": _("Incorrect code."),
        "incorrect_password": _("Incorrect password."),
        "invalid_or_expired_key": _("Invalid or expired key."),
        "invalid_password_reset": _("The password reset token was invalid."),
        "max_email_addresses": _("You cannot add more than %d email addresses."),
        "too_many_login_attempts": _(
            "Too many failed login attempts. Try again later."
        ),
        "unknown_email": _("The email address is not assigned to any user account"),
        "unverified_primary_email": _("Your primary email address must be verified."),
        "username_blacklisted": _(
            "Username can not be used. Please use other username."
        ),
        "username_password_mismatch": _(
            "The username and/or password you specified are not correct."
        ),
        "username_taken": AbstractUser._meta.get_field("username").error_messages[
            "unique"
        ],
    }

    def stash_verified_email(self, request, email):
        request.session["account_verified_email"] = email

    def unstash_verified_email(self, request):
        ret = request.session.get("account_verified_email")
        request.session["account_verified_email"] = None
        return ret

    def is_email_verified(self, request, email):
        """
        Checks whether or not the email address is already verified
        beyond allauth scope, for example, by having accepted an
        invitation before signing up.
        """
        ret = False
        verified_email = request.session.get("account_verified_email")
        if verified_email:
            ret = verified_email.lower() == email.lower()
        return ret

    def can_delete_email(self, email_address) -> bool:
        """
        Returns whether or not the given email address can be deleted.
        """
        from allauth.account.models import EmailAddress

        has_other = (
            EmailAddress.objects.filter(user_id=email_address.user_id)
            .exclude(pk=email_address.pk)
            .exists()
        )
        login_by_email = (
            app_settings.AUTHENTICATION_METHOD
            == app_settings.AuthenticationMethod.EMAIL
        )
        if email_address.primary:
            if has_other:
                # Don't allow, let the user mark one of the others as primary
                # first.
                return False
            elif login_by_email:
                # Last email & login is by email, prevent dangling account.
                return False
            return True
        elif has_other:
            # Account won't be dangling.
            return True
        elif login_by_email:
            # This is the last email.
            return False
        else:
            return True

    def format_email_subject(self, subject) -> str:
        """
        Formats the given email subject.
        """
        prefix = app_settings.EMAIL_SUBJECT_PREFIX
        if prefix is None:
            site = get_current_site(context.request)
            prefix = "[{name}] ".format(name=site.name)
        return prefix + force_str(subject)

    def get_from_email(self):
        """
        This is a hook that can be overridden to programmatically
        set the 'from' email address for sending emails
        """
        return settings.DEFAULT_FROM_EMAIL

    def render_mail(self, template_prefix, email, context, headers=None):
        """
        Renders an email to `email`.  `template_prefix` identifies the
        email that is to be sent, e.g. "account/email/email_confirmation"
        """
        to = [email] if isinstance(email, str) else email
        subject = render_to_string("{0}_subject.txt".format(template_prefix), context)
        # remove superfluous line breaks
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)

        from_email = self.get_from_email()

        bodies = {}
        html_ext = app_settings.TEMPLATE_EXTENSION
        for ext in [html_ext, "txt"]:
            try:
                template_name = "{0}_message.{1}".format(template_prefix, ext)
                bodies[ext] = render_to_string(
                    template_name,
                    context,
                    globals()["context"].request,
                ).strip()
            except TemplateDoesNotExist:
                if ext == "txt" and not bodies:
                    # We need at least one body
                    raise
        if "txt" in bodies:
            msg = EmailMultiAlternatives(
                subject, bodies["txt"], from_email, to, headers=headers
            )
            if html_ext in bodies:
                msg.attach_alternative(bodies[html_ext], "text/html")
        else:
            msg = EmailMessage(
                subject, bodies[html_ext], from_email, to, headers=headers
            )
            msg.content_subtype = "html"  # Main content is now text/html
        return msg

    def send_mail(self, template_prefix, email, context):
        ctx = {
            "email": email,
            "current_site": get_current_site(globals()["context"].request),
        }
        ctx.update(context)
        msg = self.render_mail(template_prefix, email, ctx)
        msg.send()

    def get_signup_redirect_url(self, request):
        return resolve_url(app_settings.SIGNUP_REDIRECT_URL)

    def get_login_redirect_url(self, request):
        """
        Returns the default URL to redirect to after logging in.  Note
        that URLs passed explicitly (e.g. by passing along a `next`
        GET parameter) take precedence over the value returned here.
        """
        assert request.user.is_authenticated
        url = getattr(settings, "LOGIN_REDIRECT_URLNAME", None)
        if url:
            warnings.warn(
                "LOGIN_REDIRECT_URLNAME is deprecated, simply"
                " use LOGIN_REDIRECT_URL with a URL name",
                DeprecationWarning,
            )
        else:
            url = settings.LOGIN_REDIRECT_URL
        return resolve_url(url)

    def get_logout_redirect_url(self, request):
        """
        Returns the URL to redirect to after the user logs out. Note that
        this method is also invoked if you attempt to log out while no users
        is logged in. Therefore, request.user is not guaranteed to be an
        authenticated user.
        """
        return resolve_url(app_settings.LOGOUT_REDIRECT_URL)

    def get_email_verification_redirect_url(self, email_address):
        """
        The URL to return to after email verification.
        """
        get_url = getattr(self, "get_email_confirmation_redirect_url", None)
        if get_url:
            # Deprecated.
            return get_url(self.request)

        if self.request.user.is_authenticated:
            if app_settings.EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL:
                return app_settings.EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL
            else:
                return self.get_login_redirect_url(self.request)
        else:
            return app_settings.EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL

    def get_password_change_redirect_url(self, request):
        """
        The URL to redirect to after a successful password change/set.

        NOTE: Not called during the password reset flow.
        """
        return reverse("account_change_password")

    def is_open_for_signup(self, request):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse
        """
        return True

    def new_user(self, request):
        """
        Instantiates a new User instance.
        """
        user = get_user_model()()
        return user

    def populate_username(self, request, user):
        """
        Fills in a valid username, if required and missing.  If the
        username is already present it is assumed to be valid
        (unique).
        """
        from .utils import user_email, user_field, user_username

        first_name = user_field(user, "first_name")
        last_name = user_field(user, "last_name")
        email = user_email(user)
        username = user_username(user)
        if app_settings.USER_MODEL_USERNAME_FIELD:
            user_username(
                user,
                username
                or self.generate_unique_username(
                    [first_name, last_name, email, username, "user"]
                ),
            )

    def generate_unique_username(self, txts, regex=None):
        return generate_unique_username(txts, regex)

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from .utils import user_email, user_field, user_username

        data = form.cleaned_data
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        username = data.get("username")
        user_email(user, email)
        user_username(user, username)
        if first_name:
            user_field(user, "first_name", first_name)
        if last_name:
            user_field(user, "last_name", last_name)
        if "password1" in data:
            user.set_password(data["password1"])
        elif "password" in data:
            user.set_password(data["password"])
        else:
            user.set_unusable_password()
        self.populate_username(request, user)
        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()
        return user

    def clean_username(self, username, shallow=False):
        """
        Validates the username. You can hook into this if you want to
        (dynamically) restrict what usernames can be chosen.
        """
        for validator in app_settings.USERNAME_VALIDATORS:
            validator(username)

        # TODO: Add regexp support to USERNAME_BLACKLIST
        username_blacklist_lower = [
            ub.lower() for ub in app_settings.USERNAME_BLACKLIST
        ]
        if username.lower() in username_blacklist_lower:
            raise self.validation_error("username_blacklisted")
        # Skipping database lookups when shallow is True, needed for unique
        # username generation.
        if not shallow:
            from .utils import filter_users_by_username

            if filter_users_by_username(username).exists():
                raise self.validation_error("username_taken")
        return username

    def clean_email(self, email):
        """
        Validates an email value. You can hook into this if you want to
        (dynamically) restrict what email addresses can be chosen.
        """
        return email

    def clean_password(self, password, user=None):
        """
        Validates a password. You can hook into this if you want to
        restric the allowed password choices.
        """
        min_length = app_settings.PASSWORD_MIN_LENGTH
        if min_length:
            MinimumLengthValidator(min_length).validate(password)
        validate_password(password, user)
        return password

    def validate_unique_email(self, email):
        return email

    def add_message(
        self,
        request,
        level,
        message_template=None,
        message_context=None,
        extra_tags="",
        message=None,
    ):
        """
        Wrapper of `django.contrib.messages.add_message`, that reads
        the message text from a template.
        """
        if getattr(getattr(request, "allauth", None), "headless", None):
            return
        if "django.contrib.messages" in settings.INSTALLED_APPS:
            if message:
                messages.add_message(request, level, message, extra_tags=extra_tags)
                return
            try:
                if message_context is None:
                    message_context = {}
                escaped_message = render_to_string(
                    message_template,
                    message_context,
                    context.request,
                ).strip()
                if escaped_message:
                    message = html.unescape(escaped_message)
                    messages.add_message(request, level, message, extra_tags=extra_tags)
            except TemplateDoesNotExist:
                pass

    def ajax_response(self, request, response, redirect_to=None, form=None, data=None):
        resp = {}
        status = response.status_code

        if redirect_to:
            status = 200
            resp["location"] = redirect_to
        if form:
            if request.method == "POST":
                if form.is_valid():
                    status = 200
                else:
                    status = 400
            else:
                status = 200
            resp["form"] = self.ajax_response_form(form)
            if hasattr(response, "render"):
                response.render()
            resp["html"] = response.content.decode("utf8")
        if data is not None:
            resp["data"] = data
        return HttpResponse(
            json.dumps(resp), status=status, content_type="application/json"
        )

    def ajax_response_form(self, form):
        form_spec = {
            "fields": {},
            "field_order": [],
            "errors": form.non_field_errors(),
        }
        for field in form:
            field_spec = {
                "label": force_str(field.label),
                "value": field.value(),
                "help_text": force_str(field.help_text),
                "errors": [force_str(e) for e in field.errors],
                "widget": {
                    "attrs": {
                        k: force_str(v) for k, v in field.field.widget.attrs.items()
                    }
                },
            }
            form_spec["fields"][field.html_name] = field_spec
            form_spec["field_order"].append(field.html_name)
        return form_spec

    def pre_login(
        self,
        request,
        user,
        *,
        email_verification,
        signal_kwargs,
        email,
        signup,
        redirect_url
    ):
        if not user.is_active:
            return self.respond_user_inactive(request, user)

    def post_login(
        self,
        request,
        user,
        *,
        email_verification,
        signal_kwargs,
        email,
        signup,
        redirect_url
    ):
        from .utils import get_login_redirect_url

        response = HttpResponseRedirect(
            get_login_redirect_url(request, redirect_url, signup=signup)
        )

        if signal_kwargs is None:
            signal_kwargs = {}
        signals.user_logged_in.send(
            sender=user.__class__,
            request=request,
            response=response,
            user=user,
            **signal_kwargs,
        )
        self.add_message(
            request,
            messages.SUCCESS,
            "account/messages/logged_in.txt",
            {"user": user},
        )
        return response

    def login(self, request, user):
        # HACK: This is not nice. The proper Django way is to use an
        # authentication backend
        if not hasattr(user, "backend"):
            from .auth_backends import AuthenticationBackend

            backends = get_backends()
            backend = None
            for b in backends:
                if isinstance(b, AuthenticationBackend):
                    # prefer our own backend
                    backend = b
                    break
                elif not backend and hasattr(b, "get_user"):
                    # Pick the first valid one
                    backend = b
            backend_path = ".".join([backend.__module__, backend.__class__.__name__])
            user.backend = backend_path
        django_login(request, user)

    def logout(self, request):
        django_logout(request)

    def confirm_email(self, request, email_address):
        """
        Marks the email address as confirmed on the db
        """
        from allauth.account.internal.flows import email_verification

        return email_verification.verify_email(request, email_address)

    def set_password(self, user, password) -> None:
        """
        Sets the password for the user.
        """
        user.set_password(password)
        user.save()

    def get_user_search_fields(self):
        ret = []
        User = get_user_model()
        candidates = [
            app_settings.USER_MODEL_USERNAME_FIELD,
            "first_name",
            "last_name",
            "email",
        ]
        for candidate in candidates:
            try:
                User._meta.get_field(candidate)
                ret.append(candidate)
            except FieldDoesNotExist:
                pass
        return ret

    def is_safe_url(self, url):
        from django.utils.http import url_has_allowed_host_and_scheme

        # get_host already validates the given host, so no need to check it again
        allowed_hosts = {context.request.get_host()} | set(settings.ALLOWED_HOSTS)

        if "*" in allowed_hosts:
            parsed_host = urlparse(url).netloc
            allowed_host = {parsed_host} if parsed_host else None
            return url_has_allowed_host_and_scheme(url, allowed_hosts=allowed_host)

        return url_has_allowed_host_and_scheme(url, allowed_hosts=allowed_hosts)

    def send_password_reset_mail(self, user, email, context):
        """
        Method intended to be overridden in case you need to customize the logic
        used to determine whether a user is permitted to request a password reset.
        For example, if you are enforcing something like "social only" authentication
        in your app, you may want to intervene here by checking `user.has_usable_password`

        """
        return self.send_mail("account/email/password_reset_key", email, context)

    def get_reset_password_from_key_url(self, key):
        """
        Method intended to be overridden in case the password reset email
        needs to be adjusted.
        """
        from allauth.account.internal import flows

        return flows.password_reset.get_reset_password_from_key_url(self.request, key)

    def get_email_confirmation_url(self, request, emailconfirmation):
        """Constructs the email confirmation (activation) url.

        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        from allauth.account.internal import flows

        return flows.email_verification.get_email_verification_url(
            request, emailconfirmation
        )

    def should_send_confirmation_mail(self, request, email_address, signup) -> bool:
        return True

    def send_account_already_exists_mail(self, email):
        from allauth.account.internal import flows

        signup_url = flows.signup.get_signup_url(context.request)
        password_reset_url = flows.password_reset.get_reset_password_url(
            context.request
        )
        ctx = {
            "request": context.request,
            "signup_url": signup_url,
            "password_reset_url": password_reset_url,
        }
        self.send_mail("account/email/account_already_exists", email, ctx)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        ctx = {
            "user": emailconfirmation.email_address.user,
        }
        if app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
            ctx.update({"code": emailconfirmation.key})
        else:
            ctx.update(
                {
                    "key": emailconfirmation.key,
                    "activate_url": self.get_email_confirmation_url(
                        request, emailconfirmation
                    ),
                }
            )
        if signup:
            email_template = "account/email/email_confirmation_signup"
        else:
            email_template = "account/email/email_confirmation"
        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)

    def respond_user_inactive(self, request, user):
        return headed_redirect_response("account_inactive")

    def respond_email_verification_sent(self, request, user):
        return headed_redirect_response("account_email_verification_sent")

    def _get_login_attempts_cache_key(self, request, **credentials):
        site = get_current_site(request)
        login = credentials.get("email", credentials.get("username", "")).lower()
        return "{site}:{login}".format(site=site.domain, login=login)

    def _delete_login_attempts_cached_email(self, request, **credentials):
        cache_key = self._get_login_attempts_cache_key(request, **credentials)
        ratelimit.clear(request, action="login_failed", key=cache_key)

    def pre_authenticate(self, request, **credentials):
        cache_key = self._get_login_attempts_cache_key(request, **credentials)
        if not ratelimit.consume(
            request,
            action="login_failed",
            key=cache_key,
        ):
            raise self.validation_error("too_many_login_attempts")

    def authenticate(self, request, **credentials):
        """Only authenticates, does not actually login. See `login`"""
        from allauth.account.auth_backends import AuthenticationBackend

        self.pre_authenticate(request, **credentials)
        AuthenticationBackend.unstash_authenticated_user()
        user = authenticate(request, **credentials)
        alt_user = AuthenticationBackend.unstash_authenticated_user()
        user = user or alt_user
        if user:
            self._delete_login_attempts_cached_email(request, **credentials)
        else:
            self.authentication_failed(request, **credentials)
        return user

    def authentication_failed(self, request, **credentials):
        pass

    def reauthenticate(self, user, password):
        from allauth.account.models import EmailAddress
        from allauth.account.utils import user_username

        credentials = {"password": password}
        username = user_username(user)
        if username:
            credentials["username"] = username
        email = EmailAddress.objects.get_primary_email(user)
        if email:
            credentials["email"] = email
        reauth_user = self.authenticate(context.request, **credentials)
        return reauth_user is not None and reauth_user.pk == user.pk

    def is_ajax(self, request):
        return any(
            [
                request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest",
                request.content_type == "application/json",
                request.META.get("HTTP_ACCEPT") == "application/json",
            ]
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def get_http_user_agent(self, request):
        return request.META.get("HTTP_USER_AGENT", "Unspecified")

    def generate_emailconfirmation_key(self, email):
        key = get_random_string(64).lower()
        return key

    def get_login_stages(self):
        ret = []
        ret.append("allauth.account.stages.LoginByCodeStage")
        ret.append("allauth.account.stages.EmailVerificationStage")
        if allauth_app_settings.MFA_ENABLED:
            from allauth.mfa import app_settings as mfa_settings

            ret.append("allauth.mfa.stages.AuthenticateStage")

            if mfa_settings.PASSKEY_SIGNUP_ENABLED:
                ret.append("allauth.mfa.webauthn.stages.PasskeySignupStage")
        return ret

    def get_reauthentication_methods(self, user):
        """The order of the methods returned matters. The first method is the
        default when using the `@reauthentication_required` decorator.
        """
        from allauth.account.internal.flows.reauthentication import (
            get_reauthentication_flows,
        )

        flow_by_id = {f["id"]: f for f in get_reauthentication_flows(user)}
        ret = []
        if "reauthenticate" in flow_by_id:
            entry = {
                "id": "reauthenticate",
                "description": _("Use your password"),
                "url": reverse("account_reauthenticate"),
            }
            ret.append(entry)
        if "mfa_reauthenticate" in flow_by_id:
            types = flow_by_id["mfa_reauthenticate"]["types"]
            if "recovery_codes" in types or "totp" in types:
                entry = {
                    "id": "mfa_reauthenticate",
                    "description": _("Use authenticator app or code"),
                    "url": reverse("mfa_reauthenticate"),
                }
                ret.append(entry)
            if "webauthn" in types:
                entry = {
                    "id": "mfa_reauthenticate:webauthn",
                    "description": _("Use a security key"),
                    "url": reverse("mfa_reauthenticate_webauthn"),
                }
                ret.append(entry)
        return ret

    def send_notification_mail(self, template_prefix, user, context=None, email=None):
        from allauth.account.models import EmailAddress

        if not app_settings.EMAIL_NOTIFICATIONS:
            return
        if not email:
            email = EmailAddress.objects.get_primary_email(user)
        if not email:
            return
        ctx = {
            "timestamp": timezone.now(),
            "ip": self.get_client_ip(self.request),
            "user_agent": self.get_http_user_agent(self.request),
        }
        if context:
            ctx.update(context)
        self.send_mail(template_prefix, email, ctx)

    def generate_login_code(self) -> str:
        """
        Generates a new login code.
        """
        return self._generate_code()

    def generate_email_verification_code(self) -> str:
        """
        Generates a new email verification code.
        """
        return self._generate_code()

    def _generate_code(self):
        forbidden_chars = "0OI18B2ZAEU"
        allowed_chars = string.ascii_uppercase + string.digits
        for ch in forbidden_chars:
            allowed_chars = allowed_chars.replace(ch, "")
        return get_random_string(length=6, allowed_chars=allowed_chars)

    def is_login_by_code_required(self, login) -> bool:
        """
        Returns whether or not login-by-code is required for the given
        login.
        """
        from allauth.account import authentication

        method = None
        records = authentication.get_authentication_records(self.request)
        if records:
            method = records[-1]["method"]
        if method == "code":
            return False
        value = app_settings.LOGIN_BY_CODE_REQUIRED
        if isinstance(value, bool):
            return value
        if not value:
            return False
        return method is None or method in value


def get_adapter(request=None):
    return import_attribute(app_settings.ADAPTER)(request)
