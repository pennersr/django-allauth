from typing import Optional

from django.core.exceptions import ImproperlyConfigured, PermissionDenied

from allauth.account.utils import get_next_redirect_url, get_request_param
from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.internal import statekit
from allauth.socialaccount.providers.base.constants import AuthProcess


class ProviderException(Exception):
    pass


class Provider:
    name: str  # Provided by subclasses
    id: str  # Provided by subclasses
    slug: Optional[str] = None  # Provided by subclasses

    uses_apps = True
    supports_redirect = False
    # Indicates whether or not this provider supports logging in by posting an
    # access/id-token.
    supports_token_authentication = False

    def __init__(self, request, app=None):
        self.request = request
        if self.uses_apps and app is None:
            raise ValueError("missing: app")
        self.app = app

    def __str__(self):
        return self.name

    @classmethod
    def get_slug(cls):
        return cls.slug or cls.id

    def get_login_url(self, request, next=None, **kwargs):
        """
        Builds the URL to redirect to when initiating a login for this
        provider.
        """
        raise NotImplementedError("get_login_url() for " + self.name)

    def redirect_from_request(self, request):
        kwargs = self.get_redirect_from_request_kwargs(request)
        return self.redirect(request, **kwargs)

    def get_redirect_from_request_kwargs(self, request):
        kwargs = {}
        next_url = get_next_redirect_url(request)
        if next_url:
            kwargs["next_url"] = next_url
        kwargs["process"] = get_request_param(request, "process", AuthProcess.LOGIN)
        return kwargs

    def redirect(self, request, process, next_url=None, data=None, **kwargs):
        """
        Initiate a redirect to the provider.
        """
        raise NotImplementedError()

    def verify_token(self, request, token):
        """
        Verifies the token, returning a `SocialLogin` instance when valid.
        Raises a `ValidationError` otherwise.
        """
        raise NotImplementedError()

    def media_js(self, request):
        """
        Some providers may require extra scripts (e.g. a Facebook connect)
        """
        return ""

    def wrap_account(self, social_account):
        return self.account_class(social_account)

    def get_settings(self):
        return app_settings.PROVIDERS.get(self.id, {})

    def sociallogin_from_response(self, request, response):
        """
        Instantiates and populates a `SocialLogin` model based on the data
        retrieved in `response`. The method does NOT save the model to the
        DB.

        Data for `SocialLogin` will be extracted from `response` with the
        help of the `.extract_uid()`, `.extract_extra_data()`,
        `.extract_common_fields()`, and `.extract_email_addresses()`
        methods.

        :param request: a Django `HttpRequest` object.
        :param response: object retrieved via the callback response of the
            social auth provider.
        :return: A populated instance of the `SocialLogin` model (unsaved).
        """
        # NOTE: Avoid loading models at top due to registry boot...
        from allauth.socialaccount.adapter import get_adapter
        from allauth.socialaccount.models import SocialAccount, SocialLogin

        adapter = get_adapter()
        uid = self.extract_uid(response)
        if not isinstance(uid, str):
            raise ValueError(f"uid must be a string: {repr(uid)}")
        if len(uid) > app_settings.UID_MAX_LENGTH:
            raise ImproperlyConfigured(
                f"SOCIALACCOUNT_UID_MAX_LENGTH too small (<{len(uid)})"
            )
        if not uid:
            raise ValueError("uid must be a non-empty string")

        extra_data = self.extract_extra_data(response)
        common_fields = self.extract_common_fields(response)
        socialaccount = SocialAccount(
            extra_data=extra_data,
            uid=uid,
            provider=self.sub_id,
        )
        email_addresses = self.extract_email_addresses(response)
        self.cleanup_email_addresses(
            common_fields.get("email"),
            email_addresses,
            email_verified=common_fields.get("email_verified"),
        )
        sociallogin = SocialLogin(
            account=socialaccount, email_addresses=email_addresses
        )
        user = sociallogin.user = adapter.new_user(request, sociallogin)
        user.set_unusable_password()
        adapter.populate_user(request, sociallogin, common_fields)
        return sociallogin

    def extract_uid(self, data):
        """
        Extracts the unique user ID from `data`
        """
        raise NotImplementedError(
            "The provider must implement the `extract_uid()` method"
        )

    def extract_extra_data(self, data):
        """
        Extracts fields from `data` that will be stored in
        `SocialAccount`'s `extra_data` JSONField.

        :return: any JSON-serializable Python structure.
        """
        return data

    def extract_common_fields(self, data):
        """
        Extracts fields from `data` that will be used to populate the
        `User` model in the `SOCIALACCOUNT_ADAPTER`'s `populate_user()`
        method.

        For example:

            {'first_name': 'John'}

        :return: dictionary of key-value pairs.
        """
        return {}

    def cleanup_email_addresses(self, email, addresses, email_verified=False):
        # Avoid loading models before adapters have been registered.
        from allauth.account.models import EmailAddress

        # Move user.email over to EmailAddress
        if email and email.lower() not in [a.email.lower() for a in addresses]:
            addresses.insert(
                0,
                EmailAddress(email=email, verified=bool(email_verified), primary=True),
            )
        # Force verified emails
        adapter = get_adapter()
        for address in addresses:
            if adapter.is_email_verified(self, address.email):
                address.verified = True

    def extract_email_addresses(self, data):
        """
        For example:

        [EmailAddress(email='john@example.com',
                      verified=True,
                      primary=True)]
        """
        return []

    @classmethod
    def get_package(cls):
        pkg = getattr(cls, "package", None)
        if not pkg:
            pkg = cls.__module__.rpartition(".")[0]
        return pkg

    def stash_redirect_state(
        self, request, process, next_url=None, data=None, state_id=None, **kwargs
    ):
        """
        Stashes state, returning a (random) state ID using which the state
        can be looked up later. Application specific state is stored separately
        from (core) allauth state such as `process` and `**kwargs`.
        """
        state = {"process": process, "data": data, **kwargs}
        if next_url:
            state["next"] = next_url
        return statekit.stash_state(request, state, state_id=state_id)

    def unstash_redirect_state(self, request, state_id):
        state = statekit.unstash_state(request, state_id)
        if state is None:
            raise PermissionDenied()
        return state

    @property
    def sub_id(self) -> str:
        return (
            (self.app.provider_id or self.app.provider) if self.uses_apps else self.id
        )


class ProviderAccount(object):
    def __init__(self, social_account):
        self.account = social_account

    def get_profile_url(self):
        return None

    def get_avatar_url(self):
        return None

    def get_brand(self):
        """
        Returns a dict containing an id and name identifying the
        brand. Useful when displaying logos next to accounts in
        templates.

        For most providers, these are identical to the provider. For
        OpenID however, the brand can derived from the OpenID identity
        url.
        """
        provider = self.account.get_provider()
        return dict(id=provider.id, name=provider.name)

    def __str__(self):
        return self.to_str()

    def to_str(self):
        """
        This did not use to work in the past due to py2 compatibility:

            class GoogleAccount(ProviderAccount):
                def __str__(self):
                    dflt = super(GoogleAccount, self).__str__()
                    return self.account.extra_data.get('name', dflt)

        So we have this method `to_str` that can be overridden in a conventional
        fashion, without having to worry about it.
        """
        return self.get_brand()["name"]
