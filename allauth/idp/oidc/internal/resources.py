import posixpath
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.http import HttpRequest

from oauthlib.oauth2.rfc6749.errors import OAuth2Error

from allauth.idp.oidc.adapter import get_adapter


class InvalidTargetError(OAuth2Error):
    error = "invalid_target"
    description = "The requested resource is invalid, missing, unknown, or malformed."


def get_resources(request: HttpRequest) -> list[str]:
    params = request.GET if request.method == "GET" else request.POST
    resources = params.getlist("resource")
    validate_resources(resources)
    return resources


def validate_resources(resources: list[str]) -> None:
    for resource in resources:
        parsed = urlparse(resource)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError("Resource must be an absolute URI.")
        if parsed.fragment:
            raise ValidationError("Resource must not include a fragment component.")
        if parsed.path:
            normalized_path = posixpath.normpath(parsed.path)
            if parsed.path.endswith("/") and not normalized_path.endswith("/"):
                normalized_path += "/"
            if normalized_path != parsed.path:
                raise ValidationError("Resource path is not normalized.")
        if "//" in parsed.path:
            raise ValidationError("Resource path is not normalized.")
    adapter = get_adapter()
    adapter.validate_resource_uris(uris=resources)


def is_resources_subset(requested: list[str] | None, granted: list[str] | None) -> bool:
    if not granted or not requested:
        return True
    for resource in requested:
        if not any(_is_contained_by(resource, g) for g in granted):
            return False
    return True


def _is_contained_by(resource: str, granted: str) -> bool:
    r = urlparse(resource)
    g = urlparse(granted)
    if r.scheme != g.scheme or r.netloc != g.netloc:
        return False
    g_path = g.path.rstrip("/") + "/"
    return r.path == g.path or r.path.startswith(g_path)
