from django.forms.utils import ErrorList
from django.http import JsonResponse
from django.utils.cache import add_never_cache_headers


class APIResponse(JsonResponse):
    def __init__(self, request, errors=None, data=None, meta=None, status=200):
        d = {"status": status}
        if data is not None:
            d["data"] = data
        if meta is not None:
            d["meta"] = meta
        if errors:
            d["errors"] = errors
        super().__init__(d, status=status)
        add_never_cache_headers(self)


class ErrorResponse(APIResponse):
    def __init__(self, request, exception=None, input=None, status=400):
        errors = []
        if exception is not None:
            error_datas = ErrorList(exception.error_list).get_json_data()
            errors.extend(error_datas)
        if input is not None:
            for field, error_list in input.errors.items():
                error_datas = error_list.get_json_data()
                for error_data in error_datas:
                    if field != "__all__":
                        error_data["param"] = field
                errors.extend(error_datas)
        super().__init__(request, status=status, errors=errors)
