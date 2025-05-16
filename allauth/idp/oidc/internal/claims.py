from allauth.account.models import EmailAddress
from allauth.account.utils import user_username
from allauth.idp.oidc.adapter import get_adapter


def get_claims(user, client, scopes):
    adapter = get_adapter()
    claims = {"sub": adapter.get_user_sub(client, user)}
    if "email" in scopes:
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
