import json

from django.http import QueryDict


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
