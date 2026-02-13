import ipaddress
import json
from typing import Optional
from urllib.parse import parse_qs, quote, urlencode, urlparse, urlunparse

from django import shortcuts
from django.core.exceptions import ImproperlyConfigured
from django.http import (
    HttpRequest,
    HttpResponseRedirect,
    HttpResponseServerError,
    QueryDict,
)
from django.http.request import split_domain_port
from django.urls import NoReverseMatch, reverse

from allauth import app_settings as allauth_settings


HTTP_USER_AGENT_MAX_LENGTH = 200


def serialize_request(request):
    return json.dumps(
        {
            "path": request.path,
            "path_info": request.path_info,
            "META": {k: v for k, v in request.META.items() if isinstance(v, str)},
            "GET": request.GET.urlencode(),
            "POST": request.POST.urlencode(),
            "method": request.method,
            "scheme": request.scheme,
        }
    )


def deserialize_request(s, request):
    data = json.loads(s)
    request.GET = QueryDict(data["GET"])
    request.POST = QueryDict(data["POST"])
    request.META = data["META"]
    request.path = data["path"]
    request.path_info = data["path_info"]
    request.method = data["method"]
    request._get_scheme = lambda: data["scheme"]
    return request


def redirect(to):
    try:
        return shortcuts.redirect(to)
    except NoReverseMatch:
        return shortcuts.redirect(f"/{to}")


def del_query_params(url: str, *params: str) -> str:
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query, keep_blank_values=True)
    for param in params:
        query_params.pop(param, None)
    encoded_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            encoded_query,
            parsed_url.fragment,
        )
    )
    return new_url


def add_query_params(url: str, params: dict) -> str:
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params.update(params)
    encoded_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            encoded_query,
            parsed_url.fragment,
        )
    )
    return new_url


def render_url(request, url_template, **kwargs):
    url = url_template
    for k, v in kwargs.items():
        qi = url.find("?")
        ki = url.find(f"{{{k}}}")
        if ki < 0:
            raise ImproperlyConfigured(url_template)
        is_query_param = qi >= 0 and ki > qi
        if is_query_param:
            qv = urlencode({"k": v}).partition("k=")[2]
        else:
            qv = quote(v)
        url = url.replace(f"{{{k}}}", qv)
    p = urlparse(url)
    if not p.netloc:
        url = request.build_absolute_uri(url)
    return url


def default_get_frontend_url(request, urlname, **kwargs):
    from allauth import app_settings as allauth_settings

    if allauth_settings.HEADLESS_ENABLED:
        from allauth.headless import app_settings as headless_settings

        url = headless_settings.FRONTEND_URLS.get(urlname)
        if allauth_settings.HEADLESS_ONLY and not url:
            raise ImproperlyConfigured(f"settings.HEADLESS_FRONTEND_URLS['{urlname}']")
        if url:
            return render_url(request, url, **kwargs)
    return None


def get_frontend_url(request, urlname, **kwargs):
    from allauth import app_settings as allauth_settings

    if allauth_settings.HEADLESS_ENABLED:
        from allauth.headless.adapter import get_adapter

        return get_adapter().get_frontend_url(urlname, **kwargs)
    return default_get_frontend_url(request, urlname, **kwargs)


def headed_redirect_response(viewname, query=None):
    """
    In some cases, we're redirecting to a non-headless view. In case of
    headless-only mode, that view clearly does not exist.
    """
    try:
        url = reverse(viewname)
        if query:
            url = add_query_params(url, query)
        return HttpResponseRedirect(url)
    except NoReverseMatch:
        if allauth_settings.HEADLESS_ONLY:
            # The response we would be rendering here is not actually used.
            return HttpResponseServerError()
        raise


def is_headless_request(request: HttpRequest) -> Optional[str]:
    """
    Returns the headless client type (app/browser)in case of a headless
    request.
    """
    return getattr(
        getattr(getattr(request, "allauth", None), "headless", None), "client", None
    )


def get_authorization_credential(
    request: HttpRequest, auth_scheme: str
) -> Optional[str]:
    auth = request.META.get("HTTP_AUTHORIZATION")
    if not auth:
        return None
    parts = auth.split()
    if not parts or len(parts) != 2 or parts[0].lower() != auth_scheme.lower():
        return None
    return parts[1]


def clean_client_ip(ip: str) -> Optional[str]:
    """
    Try to parse the value as an IP address to make sure it's a valid one.
    """
    try:
        domain, port = split_domain_port(ip)
        if port and domain:
            ip = domain
            # If Django splits off the port of an IPv6 address, the domain
            # has brackets.
            if ip[0] == "[" and ip[-1] == "]":
                ip = ip[1:-1]
        ip = str(ipaddress.ip_address(ip))
    except ValueError:
        return None
    else:
        return ip


def get_client_ip_from_xff(request: HttpRequest) -> Optional[str]:
    trusted_proxy_count = allauth_settings.TRUSTED_PROXY_COUNT
    xff = request.headers.get("x-forwarded-for")
    if trusted_proxy_count > 0 and xff:
        ips = xff.split(",")
        if len(ips) < trusted_proxy_count:
            raise ImproperlyConfigured(
                "ALLAUTH_TRUSTED_PROXY_COUNT does not match X-Forwarded-For"
            )
        ip = ips[-trusted_proxy_count]
    else:
        ip = None
    return ip


def get_client_ip(request: HttpRequest) -> Optional[str]:
    trusted_client_ip_header = allauth_settings.TRUSTED_CLIENT_IP_HEADER
    if trusted_client_ip_header:
        ip = request.headers.get(trusted_client_ip_header)
    else:
        ip = get_client_ip_from_xff(request)
        if not ip:
            ip = request.META["REMOTE_ADDR"]
    return clean_client_ip(ip) if ip else None
