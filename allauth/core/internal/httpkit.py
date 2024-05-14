import json
from urllib.parse import parse_qs, quote, urlencode, urlparse, urlunparse

from django import shortcuts
from django.core.exceptions import ImproperlyConfigured
from django.http import QueryDict
from django.urls import NoReverseMatch


def serialize_request(request):
    return json.dumps(
        {
            "path": request.path,
            "path_info": request.path_info,
            "META": {k: v for k, v in request.META.items() if isinstance(v, str)},
            "GET": request.GET.urlencode(),
            "POST": request.POST.urlencode(),
            "method": request.method,
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
    return request


def redirect(to):
    try:
        return shortcuts.redirect(to)
    except NoReverseMatch:
        return shortcuts.redirect(f"/{to}")


def add_query_params(url, params):
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
        ki = url.find("{" + k + "}")
        if ki < 0:
            raise ImproperlyConfigured(url_template)
        is_query_param = qi >= 0 and ki > qi
        if is_query_param:
            qv = urlencode({"k": v}).partition("k=")[2]
        else:
            qv = quote(v)
        url = url.replace("{" + k + "}", qv)
    p = urlparse(url)
    if not p.netloc:
        url = request.build_absolute_uri(url)
    return url


def get_frontend_url(request, urlname, **kwargs):
    from allauth import app_settings as allauth_settings

    if allauth_settings.HEADLESS_ENABLED:
        from allauth.headless import app_settings as headless_settings

        url = headless_settings.FRONTEND_URLS.get(urlname)
        if allauth_settings.HEADLESS_ONLY and not url:
            raise ImproperlyConfigured(f"settings.HEADLESS_FRONTEND_URLS['{urlname}']")
        if url:
            return render_url(request, url, **kwargs)
    return None
