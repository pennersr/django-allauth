import hashlib
import uuid
from typing import Any, Dict, Iterable, Literal, Optional

from django.contrib.auth import get_user_model
from django.core.management.utils import get_random_secret_key
from django.utils.translation import gettext_lazy as _

from allauth.account.internal.userkit import (
    str_to_user_id,
    user_id_to_str,
    user_username,
)
from allauth.account.models import EmailAddress
from allauth.core.internal.adapter import BaseAdapter
from allauth.core.internal.cryptokit import generate_user_code
from allauth.idp.oidc import app_settings
from allauth.utils import import_attribute


class DefaultOIDCAdapter(BaseAdapter):
    """The adapter class allows you to override various functionality of the
    ``allauth.idp.oidc`` app.  To do so, point ``settings.IDP_OIDC_ADAPTER`` to
    your own class that derives from ``DefaultOIDCAdapter`` and override the
    behavior by altering the implementation of the methods according to your own
    needs.
    """

    scope_display = {
        "openid": _("View your user ID"),
        "email": _("View your email address"),
        "profile": _("View your basic profile information"),
    }

    def generate_client_id(self) -> str:
        """
        The client ID to use for newly created clients.
        """
        return uuid.uuid4().hex

    def generate_client_secret(self) -> str:
        """
        The client secret to use for newly created clients.
        """
        return get_random_secret_key()

    def generate_user_code(self) -> str:
        return generate_user_code(length=8)

    def hash_token(self, token: str) -> str:
        """
        We don't store tokens directly, only the hash of the token. This methods generates
        that hash.
        """
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def get_issuer(self) -> str:
        """
        Returns the URL of the issuer.
        """
        return self.request.build_absolute_uri("/").rstrip("/")

    def populate_id_token(
        self, id_token: dict, client, scopes: Iterable[str], **kwargs
    ) -> None:
        """
        This method can be used to alter the ID token payload. It is already populated
        with basic values. Depending on the client and requested scopes, you can
        expose additional information here.
        """
        pass

    def populate_access_token(
        self, access_token: dict, *, client, scopes: Iterable[str], user, **kwargs
    ) -> None:
        """
        This method can be used to alter the JWT access token payload. It is already
        populated with basic values.
        """
        pass

    def get_claims(
        self,
        purpose: Literal["id_token", "userinfo"],
        user,
        client,
        scopes: Iterable[str],
        email: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Return the claims to be included in the ID token or userinfo response.
        """
        claims = {"sub": self.get_user_sub(client, user)}
        if "email" in scopes:
            if email:
                try:
                    address = EmailAddress.objects.get_for_user(user, email)
                except EmailAddress.DoesNotExist:
                    pass
            else:
                address = EmailAddress.objects.get_primary(user)
            if address:
                claims.update(
                    {
                        "email": address.email,
                        "email_verified": address.verified,
                    }
                )
        if "profile" in scopes:
            full_name = user.get_full_name()
            last_name = getattr(user, "last_name", None)
            first_name = getattr(user, "first_name", None)
            username = user_username(user)
            profile_claims = {
                "name": full_name,
                "given_name": first_name,
                "family_name": last_name,
                "preferred_username": username,
            }
            for claim_key, claim_value in profile_claims.items():
                if claim_value:
                    claims[claim_key] = claim_value
        return claims

    def get_user_sub(self, client, user) -> str:
        """
        Returns the "sub" (subject identifier) for the given user.
        """
        return user_id_to_str(user)

    def get_user_by_sub(self, client, sub: str):
        """
        Looks up a user, given its subject identifier. Returns `None` if no
        such user was found.
        """
        try:
            pk = str_to_user_id(sub)
        except ValueError:
            return None
        user = get_user_model().objects.filter(pk=pk).first()
        if not user or not user.is_active:
            return None
        return user


def get_adapter() -> DefaultOIDCAdapter:
    return import_attribute(app_settings.ADAPTER)()
