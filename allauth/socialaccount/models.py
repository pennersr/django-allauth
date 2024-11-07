from typing import Any, Dict, List, Optional

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import models
from django.utils.translation import gettext_lazy as _

import allauth.app_settings
from allauth import app_settings as allauth_settings
from allauth.account.models import EmailAddress
from allauth.account.utils import (
    filter_users_by_email,
    get_next_redirect_url,
    setup_user_email,
)
from allauth.core import context
from allauth.socialaccount import app_settings, providers, signals
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.internal import statekit
from allauth.utils import get_request_param


if not allauth_settings.SOCIALACCOUNT_ENABLED:
    raise ImproperlyConfigured(
        "allauth.socialaccount not installed, yet its models are imported."
    )


class SocialAppManager(models.Manager):
    def on_site(self, request):
        if allauth.app_settings.SITES_ENABLED:
            site = get_current_site(request)
            return self.filter(sites__id=site.id)
        return self.all()


class SocialApp(models.Model):
    objects = SocialAppManager()

    # The provider type, e.g. "google", "telegram", "saml".
    provider = models.CharField(
        verbose_name=_("provider"),
        max_length=30,
    )
    # For providers that support subproviders, such as OpenID Connect and SAML,
    # this ID identifies that instance. SocialAccount's originating from app
    # will have their `provider` field set to the `provider_id` if available,
    # else `provider`.
    provider_id = models.CharField(
        verbose_name=_("provider ID"),
        max_length=200,
        blank=True,
    )
    name = models.CharField(verbose_name=_("name"), max_length=40)
    client_id = models.CharField(
        verbose_name=_("client id"),
        max_length=191,
        help_text=_("App ID, or consumer key"),
    )
    secret = models.CharField(
        verbose_name=_("secret key"),
        max_length=191,
        blank=True,
        help_text=_("API secret, client secret, or consumer secret"),
    )
    key = models.CharField(
        verbose_name=_("key"), max_length=191, blank=True, help_text=_("Key")
    )
    settings = models.JSONField(default=dict, blank=True)

    if allauth.app_settings.SITES_ENABLED:
        # Most apps can be used across multiple domains, therefore we use
        # a ManyToManyField. Note that Facebook requires an app per domain
        # (unless the domains share a common base name).
        # blank=True allows for disabling apps without removing them
        sites = models.ManyToManyField("sites.Site", blank=True)  # type: ignore[var-annotated]

    class Meta:
        verbose_name = _("social application")
        verbose_name_plural = _("social applications")

    def __str__(self):
        return self.name

    def get_provider(self, request):
        provider_class = providers.registry.get_class(self.provider)
        return provider_class(request=request, app=self)


class SocialAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Given a `SocialApp` from which this account originates, this field equals
    # the app's `app.provider_id` if available, `app.provider` otherwise.
    provider = models.CharField(
        verbose_name=_("provider"),
        max_length=200,
    )
    # Just in case you're wondering if an OpenID identity URL is going
    # to fit in a 'uid':
    #
    # Ideally, URLField(max_length=1024, unique=True) would be used
    # for identity.  However, MySQL has a max_length limitation of 191
    # for URLField (in case of utf8mb4). How about
    # models.TextField(unique=True) then?  Well, that won't work
    # either for MySQL due to another bug[1]. So the only way out
    # would be to drop the unique constraint, or switch to shorter
    # identity URLs. Opted for the latter, as [2] suggests that
    # identity URLs are supposed to be short anyway, at least for the
    # old spec.
    #
    # [1] http://code.djangoproject.com/ticket/2495.
    # [2] http://openid.net/specs/openid-authentication-1_1.html#limits

    uid = models.CharField(
        verbose_name=_("uid"), max_length=app_settings.UID_MAX_LENGTH
    )
    last_login = models.DateTimeField(verbose_name=_("last login"), auto_now=True)
    date_joined = models.DateTimeField(verbose_name=_("date joined"), auto_now_add=True)
    extra_data = models.JSONField(verbose_name=_("extra data"), default=dict)

    class Meta:
        unique_together = ("provider", "uid")
        verbose_name = _("social account")
        verbose_name_plural = _("social accounts")

    def authenticate(self):
        return authenticate(account=self)

    def __str__(self):
        from .helpers import socialaccount_user_display

        return socialaccount_user_display(self)

    def get_profile_url(self):
        return self.get_provider_account().get_profile_url()

    def get_avatar_url(self):
        return self.get_provider_account().get_avatar_url()

    def get_provider(self, request=None):
        provider = getattr(self, "_provider", None)
        if provider:
            return provider
        adapter = get_adapter()
        provider = self._provider = adapter.get_provider(
            request or context.request, provider=self.provider
        )
        return provider

    def get_provider_account(self):
        return self.get_provider().wrap_account(self)


class SocialToken(models.Model):
    app = models.ForeignKey(SocialApp, on_delete=models.SET_NULL, blank=True, null=True)
    account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    token = models.TextField(
        verbose_name=_("token"),
        help_text=_('"oauth_token" (OAuth1) or access token (OAuth2)'),
    )
    token_secret = models.TextField(
        blank=True,
        verbose_name=_("token secret"),
        help_text=_('"oauth_token_secret" (OAuth1) or refresh token (OAuth2)'),
    )
    expires_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("expires at")
    )

    class Meta:
        unique_together = ("app", "account")
        verbose_name = _("social application token")
        verbose_name_plural = _("social application tokens")

    def __str__(self):
        return "%s (%s)" % (self._meta.verbose_name, self.pk)


class SocialLogin:
    """
    Represents a social user that is in the process of being logged
    in. This consists of the following information:

    `account` (`SocialAccount` instance): The social account being
    logged in. Providers are not responsible for checking whether or
    not an account already exists or not. Therefore, a provider
    typically creates a new (unsaved) `SocialAccount` instance. The
    `User` instance pointed to by the account (`account.user`) may be
    prefilled by the provider for use as a starting point later on
    during the signup process.

    `token` (`SocialToken` instance): An optional access token token
    that results from performing a successful authentication
    handshake.

    `state` (`dict`): The state to be preserved during the
    authentication handshake. Note that this state may end up in the
    url -- do not put any secrets in here. It currently only contains
    the url to redirect to after login.

    `email_addresses` (list of `EmailAddress`): Optional list of
    email addresses retrieved from the provider.
    """

    account: SocialAccount
    token: Optional[SocialToken]
    email_addresses: List[EmailAddress]
    state: Dict
    _did_authenticate_by_email: Optional[str]

    def __init__(
        self,
        user=None,
        account: Optional[SocialAccount] = None,
        token: Optional[SocialToken] = None,
        email_addresses: Optional[List[EmailAddress]] = None,
    ):
        if token:
            assert token.account is None or token.account == account  # nosec
        self.token = token
        self.user = user
        if account:
            self.account = account
        self.email_addresses = email_addresses if email_addresses else []
        self.state = {}

    def connect(self, request, user) -> None:
        self.user = user
        self.save(request, connect=True)
        signals.social_account_added.send(
            sender=SocialLogin, request=request, sociallogin=self
        )

        get_adapter().send_notification_mail(
            "socialaccount/email/account_connected",
            self.user,
            context={
                "account": self.account,
                "provider": self.account.get_provider(),
            },
        )

    @property
    def is_headless(self) -> bool:
        return bool(self.state.get("headless"))

    def serialize(self) -> Dict[str, Any]:
        serialize_instance = get_adapter().serialize_instance
        ret = dict(
            account=serialize_instance(self.account),
            user=serialize_instance(self.user),
            state=self.state,
            email_addresses=[serialize_instance(ea) for ea in self.email_addresses],
        )
        if self.token:
            ret["token"] = serialize_instance(self.token)
        return ret

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "SocialLogin":
        deserialize_instance = get_adapter().deserialize_instance
        account = deserialize_instance(SocialAccount, data["account"])
        user = deserialize_instance(get_user_model(), data["user"])
        if "token" in data:
            token = deserialize_instance(SocialToken, data["token"])
        else:
            token = None
        email_addresses = []
        for ea in data["email_addresses"]:
            email_address = deserialize_instance(EmailAddress, ea)
            email_addresses.append(email_address)
        ret = cls()
        ret.token = token
        ret.account = account
        ret.user = user
        ret.email_addresses = email_addresses
        ret.state = data["state"]
        return ret

    def save(self, request, connect: bool = False) -> None:
        """
        Saves a new account. Note that while the account is new,
        the user may be an existing one (when connecting accounts)
        """
        user = self.user
        user.save()
        self.account.user = user
        self.account.save()
        if app_settings.STORE_TOKENS and self.token:
            self.token.account = self.account
            self.token.save()
        if connect:
            # TODO: Add any new email addresses automatically?
            pass
        else:
            setup_user_email(request, user, self.email_addresses)

    @property
    def is_existing(self) -> bool:
        """When `False`, this social login represents a temporary account, not
        yet backed by a database record.
        """
        if self.user.pk is None:
            return False
        return get_user_model().objects.filter(pk=self.user.pk).exists()

    def lookup(self) -> None:
        """Look up the existing local user account to which this social login
        points, if any.
        """
        self._did_authenticate_by_email = None
        if not self._lookup_by_socialaccount():
            self._lookup_by_email()

    def _lookup_by_socialaccount(self) -> bool:
        assert not self.is_existing  # nosec
        try:
            a = SocialAccount.objects.get(
                provider=self.account.provider, uid=self.account.uid
            )
            # Update account
            a.extra_data = self.account.extra_data
            self.account = a
            self.user = self.account.user
            a.save()
            signals.social_account_updated.send(
                sender=SocialLogin, request=context.request, sociallogin=self
            )
            self._store_token()
            return True
        except SocialAccount.DoesNotExist:
            return False

    def _store_token(self) -> None:
        # Update token
        if not app_settings.STORE_TOKENS or not self.token:
            return
        assert not self.token.pk  # nosec
        app = self.token.app
        if app and not app.pk:
            # If the app is not stored in the db, leave the FK empty.
            app = None
        try:
            t = SocialToken.objects.get(account=self.account, app=app)
            t.token = self.token.token
            if self.token.token_secret:
                # only update the refresh token if we got one
                # many oauth2 providers do not resend the refresh token
                t.token_secret = self.token.token_secret
            t.expires_at = self.token.expires_at
            t.save()
            self.token = t
        except SocialToken.DoesNotExist:
            self.token.account = self.account
            self.token.app = app
            self.token.save()

    def _lookup_by_email(self) -> None:
        emails = [e.email for e in self.email_addresses if e.verified]
        for email in emails:
            if not get_adapter().can_authenticate_by_email(self, email):
                continue
            users = filter_users_by_email(email, prefer_verified=True)
            if users:
                self.user = users[0]
                self._did_authenticate_by_email = email
                return

    def _accept_login(self, request) -> None:
        from allauth.socialaccount.internal.flows.email_authentication import (
            wipe_password,
        )

        if self._did_authenticate_by_email:
            wipe_password(request, self.user, self._did_authenticate_by_email)
            if app_settings.EMAIL_AUTHENTICATION_AUTO_CONNECT:
                self.connect(context.request, self.user)

    def get_redirect_url(self, request) -> Optional[str]:
        url = self.state.get("next")
        return url

    @classmethod
    def state_from_request(cls, request) -> Dict[str, Any]:
        """
        TODO: Deprecated! To be integrated with provider.redirect()
        """
        state = {}
        next_url = get_next_redirect_url(request)
        if next_url:
            state["next"] = next_url
        state["process"] = get_request_param(request, "process", "login")
        state["scope"] = get_request_param(request, "scope", "")
        state["auth_params"] = get_request_param(request, "auth_params", "")
        return state

    @classmethod
    def stash_state(cls, request, state: Optional[Dict[str, Any]] = None) -> str:
        if state is None:
            # Only for providers that don't support redirect() yet.
            state = cls.state_from_request(request)
        return statekit.stash_state(request, state)

    @classmethod
    def unstash_state(cls, request) -> Optional[Dict[str, Any]]:
        state = statekit.unstash_last_state(request)
        if state is None:
            raise PermissionDenied()
        return state
