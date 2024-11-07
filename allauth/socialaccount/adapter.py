import functools
import warnings

from django.core.exceptions import (
    ImproperlyConfigured,
    MultipleObjectsReturned,
)
from django.db.models import Q
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.utils import user_email, user_field, user_username
from allauth.core.internal.adapter import BaseAdapter
from allauth.utils import (
    deserialize_instance,
    import_attribute,
    serialize_instance,
    valid_email_or_none,
)

from . import app_settings


class DefaultSocialAccountAdapter(BaseAdapter):
    """The adapter class allows you to override various functionality of the
    ``allauth.socialaccount`` app.  To do so, point ``settings.SOCIALACCOUNT_ADAPTER`` to
    your own class that derives from ``DefaultSocialAccountAdapter`` and override the
    behavior by altering the implementation of the methods according to your own
    needs.
    """

    error_messages = {
        "email_taken": _(
            "An account already exists with this email address."
            " Please sign in to that account first, then connect"
            " your %s account."
        ),
        "invalid_token": _("Invalid token."),
        "no_password": _("Your account has no password set up."),
        "no_verified_email": _("Your account has no verified email address."),
        "disconnect_last": _(
            "You cannot disconnect your last remaining third-party account."
        ),
        "connected_other": _(
            "The third-party account is already connected to a different account."
        ),
    }

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        You can use this hook to intervene, e.g. abort the login by
        raising an ImmediateHttpResponse

        Why both an adapter hook and the signal? Intervening in
        e.g. the flow from within a signal handler is bad -- multiple
        handlers may be active and are executed in undetermined order.
        """
        pass

    def on_authentication_error(
        self,
        request,
        provider,
        error=None,
        exception=None,
        extra_context=None,
    ):
        """
        Invoked when there is an error in the authentication cycle. In this
        case, pre_social_login will not be reached.

        You can use this hook to intervene, e.g. redirect to an
        educational flow by raising an ImmediateHttpResponse.
        """
        if hasattr(self, "authentication_error"):
            warnings.warn(
                "adapter.authentication_error() is deprecated, use adapter.on_authentication_error()"
            )

            self.authentication_error(
                request,
                provider.id,
                error=error,
                exception=exception,
                extra_context=extra_context,
            )

    def new_user(self, request, sociallogin):
        """
        Instantiates a new User instance.
        """
        return get_account_adapter().new_user(request)

    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login. In case of auto-signup,
        the signup form is not available.
        """
        u = sociallogin.user
        u.set_unusable_password()
        if form:
            get_account_adapter().save_user(request, u, form)
        else:
            get_account_adapter().populate_username(request, u)
        sociallogin.save(request)
        return u

    def populate_user(self, request, sociallogin, data):
        """
        Hook that can be used to further populate the user instance.

        For convenience, we populate several common fields.

        Note that the user instance being populated represents a
        suggested User instance that represents the social user that is
        in the process of being logged in.

        The User instance need not be completely valid and conflict
        free. For example, verifying whether or not the username
        already exists, is not a responsibility.
        """
        username = data.get("username")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        name = data.get("name")
        user = sociallogin.user
        user_username(user, username or "")
        user_email(user, valid_email_or_none(email) or "")
        name_parts = (name or "").partition(" ")
        user_field(user, "first_name", first_name or name_parts[0])
        user_field(user, "last_name", last_name or name_parts[2])
        return user

    def get_connect_redirect_url(self, request, socialaccount):
        """
        Returns the default URL to redirect to after successfully
        connecting a social account.
        """
        url = reverse("socialaccount_connections")
        return url

    def validate_disconnect(self, account, accounts) -> None:
        """
        Validate whether or not the socialaccount account can be
        safely disconnected.
        """
        pass

    def is_auto_signup_allowed(self, request, sociallogin):
        # If email is specified, check for duplicate and if so, no auto signup.
        auto_signup = app_settings.AUTO_SIGNUP
        return auto_signup

    def is_open_for_signup(self, request, sociallogin):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse
        """
        return get_account_adapter(request).is_open_for_signup(request)

    def get_signup_form_initial_data(self, sociallogin):
        user = sociallogin.user
        initial = {
            "email": user_email(user) or "",
            "username": user_username(user) or "",
            "first_name": user_field(user, "first_name") or "",
            "last_name": user_field(user, "last_name") or "",
        }
        return initial

    def deserialize_instance(self, model, data):
        return deserialize_instance(model, data)

    def serialize_instance(self, instance):
        return serialize_instance(instance)

    def list_providers(self, request):
        from allauth.socialaccount.providers import registry

        ret = []
        provider_classes = registry.get_class_list()
        apps = self.list_apps(request)
        apps_map = {}
        for app in apps:
            apps_map.setdefault(app.provider, []).append(app)
        for provider_class in provider_classes:
            provider_apps = apps_map.get(provider_class.id, [])
            if not provider_apps:
                if provider_class.uses_apps:
                    continue
                provider_apps = [None]
            for app in provider_apps:
                provider = provider_class(request=request, app=app)
                ret.append(provider)
        return ret

    def get_provider(self, request, provider, client_id=None):
        """Looks up a `provider`, supporting subproviders by looking up by
        `provider_id`.
        """
        from allauth.socialaccount.providers import registry

        provider_class = registry.get_class(provider)
        if provider_class is None or provider_class.uses_apps:
            app = self.get_app(request, provider=provider, client_id=client_id)
            if not provider_class:
                # In this case, the `provider` argument passed was a
                # `provider_id`.
                provider_class = registry.get_class(app.provider)
            if not provider_class:
                raise ImproperlyConfigured(f"unknown provider: {app.provider}")
            return provider_class(request, app=app)
        elif provider_class:
            assert not provider_class.uses_apps  # nosec
            return provider_class(request, app=None)
        else:
            raise ImproperlyConfigured(f"unknown provider: {app.provider}")

    def list_apps(self, request, provider=None, client_id=None):
        """SocialApp's can be setup in the database, or, via
        `settings.SOCIALACCOUNT_PROVIDERS`.  This methods returns a uniform list
        of all known apps matching the specified criteria, and blends both
        (db/settings) sources of data.
        """
        # NOTE: Avoid loading models at top due to registry boot...
        from allauth.socialaccount.models import SocialApp

        # Map provider to the list of apps.
        provider_to_apps = {}

        # First, populate it with the DB backed apps.
        if request:
            db_apps = SocialApp.objects.on_site(request)
        else:
            db_apps = SocialApp.objects.all()
        if provider:
            db_apps = db_apps.filter(Q(provider=provider) | Q(provider_id=provider))
        if client_id:
            db_apps = db_apps.filter(client_id=client_id)
        for app in db_apps:
            apps = provider_to_apps.setdefault(app.provider, [])
            apps.append(app)

        # Then, extend it with the settings backed apps.
        for p, pcfg in app_settings.PROVIDERS.items():
            app_configs = pcfg.get("APPS")
            if app_configs is None:
                app_config = pcfg.get("APP")
                if app_config is None:
                    continue
                app_configs = [app_config]

            apps = provider_to_apps.setdefault(p, [])
            for config in app_configs:
                app = SocialApp(provider=p)
                for field in [
                    "name",
                    "provider_id",
                    "client_id",
                    "secret",
                    "key",
                    "settings",
                ]:
                    if field in config:
                        setattr(app, field, config[field])
                if "certificate_key" in config:
                    warnings.warn("'certificate_key' should be moved into app.settings")
                    app.settings["certificate_key"] = config["certificate_key"]
                if client_id and app.client_id != client_id:
                    continue
                if (
                    provider
                    and app.provider_id != provider
                    and app.provider != provider
                ):
                    continue
                apps.append(app)

        # Flatten the list of apps.
        apps = []
        for provider_apps in provider_to_apps.values():
            apps.extend(provider_apps)
        return apps

    def get_app(self, request, provider, client_id=None):
        from allauth.socialaccount.models import SocialApp

        apps = self.list_apps(request, provider=provider, client_id=client_id)
        if len(apps) > 1:
            visible_apps = [app for app in apps if not app.settings.get("hidden")]
            if len(visible_apps) != 1:
                raise MultipleObjectsReturned
            apps = visible_apps
        elif len(apps) == 0:
            raise SocialApp.DoesNotExist()
        return apps[0]

    def send_notification_mail(self, *args, **kwargs):
        return get_account_adapter().send_notification_mail(*args, **kwargs)

    def get_requests_session(self):
        import requests

        session = requests.Session()
        session.request = functools.partial(
            session.request, timeout=app_settings.REQUESTS_TIMEOUT
        )
        return session

    def is_email_verified(self, provider, email):
        """
        Returns ``True`` iff the given email encountered during a social
        login for the given provider is to be assumed verified.

        This can be configured with a ``"verified_email"`` key in the provider
        app settings, or a ``"VERIFIED_EMAIL"`` in the global provider settings
        (``SOCIALACCOUNT_PROVIDERS``).  Both can be set to ``False`` or
        ``True``, or, a list of domains to match email addresses against.
        """
        verified_email = None
        if provider.app:
            verified_email = provider.app.settings.get("verified_email")
        if verified_email is None:
            settings = provider.get_settings()
            verified_email = settings.get("VERIFIED_EMAIL", False)
        if isinstance(verified_email, bool):
            pass
        elif isinstance(verified_email, list):
            email_domain = email.partition("@")[2].lower()
            verified_domains = [d.lower() for d in verified_email]
            verified_email = email_domain in verified_domains
        else:
            raise ImproperlyConfigured("verified_email wrongly configured")
        return verified_email

    def can_authenticate_by_email(self, login, email):
        """
        Returns ``True`` iff  authentication by email is active for this login/email.

        This can be configured with a ``"email_authentication"`` key in the provider
        app settings, or a ``"VERIFIED_EMAIL"`` in the global provider settings
        (``SOCIALACCOUNT_PROVIDERS``).
        """
        ret = None
        provider = login.account.get_provider()
        if provider.app:
            ret = provider.app.settings.get("email_authentication")
        if ret is None:
            ret = app_settings.EMAIL_AUTHENTICATION or provider.get_settings().get(
                "EMAIL_AUTHENTICATION", False
            )
        return ret

    def generate_state_param(self, state: dict) -> str:
        """
        To preserve certain state before the handshake with the provider
        takes place, and be able to verify/use that state later on, a `state`
        parameter is typically passed to the provider. By default, a random
        string sufficies as the state parameter value is actually just a
        reference/pointer to the actual state. You can use this adapter method
        to alter the generation of the `state` parameter.
        """
        from allauth.socialaccount.internal.statekit import STATE_ID_LENGTH

        return get_random_string(STATE_ID_LENGTH)


def get_adapter(request=None):
    return import_attribute(app_settings.ADAPTER)(request)
