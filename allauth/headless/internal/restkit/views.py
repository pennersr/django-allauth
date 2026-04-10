from __future__ import annotations

import json
from typing import Any

from django.http import HttpRequest, HttpResponseBadRequest, HttpResponseBase
from django.views.generic import View

from allauth.core.exceptions import ImmediateHttpResponse
from allauth.headless.internal.restkit.inputs import Input
from allauth.headless.internal.restkit.response import ErrorResponse


class RESTView(View):
    input_class: dict[str, type[Input]] | None | type[Input] = None
    handle_json_input = True

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        return self.handle(request, *args, **kwargs)

    def handle(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        if self.handle_json_input and request.method != "GET":
            self.data = self._parse_json(request)
            response = self.handle_input(self.data)
            if response:
                return response
        return super().dispatch(request, *args, **kwargs)

    def get_input_class(self) -> type[Input] | None:
        input_class = self.input_class
        if isinstance(input_class, dict):
            input_class = input_class.get(self.request.method)  # type:ignore[arg-type]
        return input_class

    def get_input_kwargs(self) -> dict:
        return {}

    def handle_input(self, data) -> ErrorResponse | None:
        input_class = self.get_input_class()
        if not input_class:
            return None
        input_kwargs = self.get_input_kwargs()
        if data is None:
            # Make form bound on empty POST
            data = {}
        self.input = input_class(data=data, **input_kwargs)
        if not self.input.is_valid():
            return self.handle_invalid_input(self.input)
        return None

    def handle_invalid_input(self, input) -> ErrorResponse:
        return ErrorResponse(self.request, input=input)

    def _parse_json(self, request: HttpRequest):
        if request.method == "GET" or not request.body:
            return
        try:
            return json.loads(request.body.decode("utf8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ImmediateHttpResponse(response=HttpResponseBadRequest())
