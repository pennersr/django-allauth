from typing import Dict, Tuple
from urllib.parse import urlparse, urlunparse

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from oauthlib.common import quote, urlencode, urlencoded
from oauthlib.oauth2.rfc6749.errors import OAuth2Error

from allauth.account import app_settings as account_settings


def get_uri(request: HttpRequest) -> str:
    """
    Django considers "safe" some characters that aren't so for oauthlib.
    We have to search for them and properly escape.
    """
    parsed = list(urlparse(request.get_full_path()))
    unsafe = set(c for c in parsed[4]).difference(urlencoded)
    for c in unsafe:
        parsed[4] = parsed[4].replace(c, quote(c, safe=b""))

    return urlunparse(parsed)


def extract_params(request: HttpRequest) -> Tuple[str, str, str, Dict[str, str]]:
    uri = get_uri(request)
    body: str = urlencode(request.POST.items())
    headers = extract_headers(request)
    if request.method is None:
        raise ValueError(request.method)
    return uri, request.method, body, headers


def extract_headers(request) -> Dict[str, str]:
    """
    You need to define extract_params and make sure it does not include file
    like objects waiting for input. In Django this is request.META['wsgi.input']
    and request.META['wsgi.errors']
    """
    headers = request.META.copy()
    headers.pop("wsgi.input", None)
    headers.pop("wsgi.errors", None)
    if "HTTP_AUTHORIZATION" in headers:
        headers["Authorization"] = headers["HTTP_AUTHORIZATION"]
    if "HTTP_ORIGIN" in headers:
        headers["Origin"] = headers["HTTP_ORIGIN"]
    if "CONTENT_TYPE" in headers:
        headers["Content-Type"] = headers["CONTENT_TYPE"]
    return headers


def convert_response(headers, body, status):
    if isinstance(body, dict):
        response = JsonResponse(body, status=status)
    else:
        response = HttpResponse(content=body, status=status)
    for k, v in headers.items():
        response[k] = v
    return response


def respond_html_error(request: HttpRequest, error: OAuth2Error) -> HttpResponse:
    context = {"error": error}
    return render(
        request,
        "idp/oidc/error." + account_settings.TEMPLATE_EXTENSION,
        context,
    )


def respond_json_error(request: HttpRequest, error: OAuth2Error) -> HttpResponse:
    response = HttpResponse(
        error.json, status=error.status_code, content_type="application/json"
    )
    for k, v in error.headers.items():
        response[k] = v
    return response
