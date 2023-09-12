from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.urls import reverse

from onelogin.saml2.constants import OneLogin_Saml2_Constants
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialApp

from .provider import SAMLProvider


def get_app_or_404(request, organization_slug):
    adapter = get_adapter()
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


def build_sp_config(request, provider_config, org):
    acs_url = request.build_absolute_uri(reverse("saml_acs", args=[org]))
    sls_url = request.build_absolute_uri(reverse("saml_sls", args=[org]))
    metadata_url = request.build_absolute_uri(reverse("saml_metadata", args=[org]))
    sp_config = {
        "entityId": metadata_url,
        "assertionConsumerService": {
            "url": acs_url,
            "binding": OneLogin_Saml2_Constants.BINDING_HTTP_POST,
        },
        "singleLogoutService": {
            "url": sls_url,
            "binding": OneLogin_Saml2_Constants.BINDING_HTTP_REDIRECT,
        },
    }
    avd = provider_config.get("advanced", {})
    if avd.get("x509cert") is not None:
        sp_config["x509cert"] = avd["x509cert"]

    if avd.get("x509cert_new"):
        sp_config["x509certNew"] = avd["x509cert_new"]

    if avd.get("private_key") is not None:
        sp_config["privateKey"] = avd["private_key"]

    if avd.get("name_id_format") is not None:
        sp_config["NameIDFormat"] = avd["name_id_format"]

    return sp_config


def fetch_metadata_url_config(idp_config):
    metadata_url = idp_config["metadata_url"]
    entity_id = idp_config["entity_id"]
    cache_key = f"saml.metadata.{metadata_url}.{entity_id}"
    saml_config = cache.get(cache_key)
    if saml_config is None:
        saml_config = OneLogin_Saml2_IdPMetadataParser.parse_remote(
            metadata_url,
            entity_id=entity_id,
            timeout=idp_config.get("metadata_request_timeout", 10),
        )
        cache.set(
            cache_key,
            saml_config,
            idp_config.get("metadata_cache_timeout", 60 * 60 * 4),
        )
    return saml_config


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
        "nameIdEncrypted": avd.get("name_id_encrypted", False),
        "wantNameIdEncrypted": avd.get("want_name_id_encrypted", False),
        "allowSingleLabelDomains": avd.get("allow_single_label_domains", False),
        "rejectDeprecatedAlgorithm": avd.get("reject_deprecated_algorithm", True),
        "wantNameId": avd.get("want_name_id", False),
        "wantAttributeStatement": avd.get("want_attribute_statement", True),
        "allowRepeatAttributeName": avd.get("allow_repeat_attribute_name", True),
    }
    saml_config = {
        "strict": avd.get("strict", True),
        "security": security_config,
    }

    contact_person = provider_config.get("contact_person")
    if contact_person:
        saml_config["contactPerson"] = contact_person

    organization = provider_config.get("organization")
    if organization:
        saml_config["organization"] = organization

    idp = provider_config.get("idp")
    if idp is None:
        raise ImproperlyConfigured("`idp` missing")
    metadata_url = idp.get("metadata_url")
    if metadata_url:
        meta_config = fetch_metadata_url_config(idp)
        saml_config["idp"] = meta_config["idp"]
    else:
        saml_config["idp"] = {
            "entityId": idp["entity_id"],
            "x509cert": idp["x509cert"],
            "singleSignOnService": {"url": idp["sso_url"]},
        }
        slo_url = idp.get("slo_url")
        if slo_url:
            saml_config["idp"]["singleLogoutService"] = {"url": slo_url}

    saml_config["sp"] = build_sp_config(request, provider_config, org)
    return saml_config
