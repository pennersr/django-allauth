import json
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django import shortcuts
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
