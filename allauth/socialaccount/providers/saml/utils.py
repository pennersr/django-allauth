from django.http import Http404
from django.urls import reverse

from onelogin.saml2.constants import OneLogin_Saml2_Constants

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialApp

from .provider import SAMLProvider


def get_app_or_404(request, organization_slug):
    adapter = get_adapter(request)
    try:
        return adapter.get_app(
            request, provider=SAMLProvider.id, client_id=organization_slug
        )
    except SocialApp.DoesNotExist:
        raise Http404(f"no SocialApp found with client_id={organization_slug}")


def prepare_django_request(request):
    result = {
        "https": "on" if request.is_secure() else "off",
        "http_host": request.META["HTTP_HOST"],
        "script_name": request.META["PATH_INFO"],
        "get_data": request.GET.copy(),
        # 'lowercase_urlencoding': True,
        "post_data": request.POST.copy(),
    }
    return result


def build_saml_config(request, provider_config, org):
    avd = provider_config.get("advanced", {})

    security_config = {
        "authnRequestsSigned": avd.get("authn_request_signed", False),
        "digestAlgorithm": avd.get("digest_algorithm", OneLogin_Saml2_Constants.SHA256),
        "logoutRequestSigned": avd.get("logout_request_signed", False),
        "logoutResponseSigned": avd.get("logout_response_signed", False),
        "requestedAuthnContext": False,
        "signatureAlgorithm": avd.get(
            "signature_algorithm", OneLogin_Saml2_Constants.RSA_SHA256
        ),
        "signMetadata": avd.get("metadata_signed", False),
        "wantAssertionsEncrypted": avd.get("want_assertion_encrypted", False),
        "wantAssertionsSigned": avd.get("want_assertion_signed", False),
        "wantMessagesSigned": avd.get("want_message_signed", False),
        "wantNameId": False,
    }
    acs_url = request.build_absolute_uri(reverse("saml_acs", args=[org]))
    sls_url = request.build_absolute_uri(reverse("saml_sls", args=[org]))
    metadata_url = request.build_absolute_uri(reverse("saml_metadata", args=[org]))
    saml_config = {
        "strict": avd.get("strict", True),
        "sp": {
            "entityId": metadata_url,
            "assertionConsumerService": {
                "url": acs_url,
                "binding": OneLogin_Saml2_Constants.BINDING_HTTP_POST,
            },
            "singleLogoutService": {
                "url": sls_url,
                "binding": OneLogin_Saml2_Constants.BINDING_HTTP_REDIRECT,
            },
        },
        "security": security_config,
    }

    idp = provider_config.get("idp")

    if idp is not None:
        saml_config["idp"] = {
            "entityId": idp["entity_id"],
            "x509cert": idp["x509cert"],
            "singleSignOnService": {"url": idp["sso_url"]},
            "singleLogoutService": {"url": idp["slo_url"]},
        }

    if avd.get("x509cert") is not None:
        saml_config["sp"]["x509cert"] = avd["x509cert"]

    if avd.get("private_key") is not None:
        saml_config["sp"]["privateKey"] = avd["private_key"]

    return saml_config
