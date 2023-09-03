from __future__ import absolute_import

from django.core.exceptions import (
    ImproperlyConfigured,
    MultipleObjectsReturned,
    ValidationError,
)
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from allauth.core import context

from ..account.adapter import get_adapter as get_account_adapter
from ..account.app_settings import EmailVerificationMethod
from ..account.models import EmailAddress
from ..account.utils import user_email, user_field, user_username
from ..utils import (
    deserialize_instance,
    import_attribute,
    serialize_instance,
    valid_email_or_none,
)
from . import app_settings


class DefaultSocialAccountAdapter(object):
    error_messages = {
        "email_taken": _(
            "An account already exists with this email address."
            " Please sign in to that account first, then connect"
            " your %s account."
        )
    }

    def __init__(self, request=None):
        # Explicitly passing `request` is deprecated, just use:
        # `allauth.core.context.request`.
        self.request = context.request

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

    def authentication_error(
        self,
        request,
        provider_id,
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
        pass

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

    def validate_disconnect(self, account, accounts):
        """
        Validate whether or not the socialaccount account can be
        safely disconnected.
        """
        if len(accounts) == 1:
            # No usable password would render the local account unusable
            if not account.user.has_usable_password():
                raise ValidationError(_("Your account has no password set up."))
            # No email address, no password reset
            if app_settings.EMAIL_VERIFICATION == EmailVerificationMethod.MANDATORY:
                if not EmailAddress.objects.filter(
                    user=account.user, verified=True
                ).exists():
                    raise ValidationError(
                        _("Your account has no verified email address.")
                    )

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

    def get_provider(self, request, provider):
        """Looks up a `provider`, supporting subproviders by looking up by
        `provider_id`.
        """
        from allauth.socialaccount.providers import registry

        provider_class = registry.get_class(provider)
        if provider_class is None or provider_class.uses_apps:
            app = self.get_app(request, provider=provider)
            if not provider_class:
                # In this case, the `provider` argument passed was a
                # `provider_id`.
                provider_class = registry.get_class(app.provider)
            if not provider_class:
                raise ImproperlyConfigured(f"unknown provider: {app.provider}")
            return provider_class(request, app=app)
        elif provider_class:
            assert not provider_class.uses_apps
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
        db_apps = SocialApp.objects.on_site(request)
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
                    "certificate_key",
                    "settings",
                ]:
                    if field in config:
                        setattr(app, field, config[field])
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
            raise MultipleObjectsReturned
        elif len(apps) == 0:
            raise SocialApp.DoesNotExist()
        return apps[0]


def get_adapter(request=None):
    return import_attribute(app_settings.ADAPTER)(request)
