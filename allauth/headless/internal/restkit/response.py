from __future__ import annotations

from http import HTTPStatus
from typing import Any

from django.forms.utils import ErrorList
from django.http import HttpRequest, JsonResponse
from django.utils.cache import add_never_cache_headers

from allauth.headless.internal import authkit, sessionkit


class APIResponse(JsonResponse):
    def __init__(
        self,
        request: HttpRequest,
        errors=None,
        data=None,
        meta: dict | None = None,
        status: int = HTTPStatus.OK,
    ) -> None:
        d: dict[str, Any] = {"status": status}
        if data is not None:
            d["data"] = data
        meta = self._add_session_meta(request, meta)
        if meta is not None:
            d["meta"] = meta
        if errors:
            d["errors"] = errors
        super().__init__(d, status=status)
        add_never_cache_headers(self)

    def _add_session_meta(self, request: HttpRequest, meta: dict | None) -> dict | None:
        session_token = sessionkit.expose_session_token(request)
        access_token_payload = authkit.expose_access_token(request)
        if session_token:
            meta = meta or {}
            meta["session_token"] = session_token
        if access_token_payload:
            meta = meta or {}
            meta.update(access_token_payload)
        return meta


class ErrorResponse(APIResponse):
    def __init__(
        self,
        request: HttpRequest,
        exception=None,
        input=None,
        status=HTTPStatus.BAD_REQUEST,
    ) -> None:
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
