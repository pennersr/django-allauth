import json

from django.http import HttpResponseBadRequest
from django.views.generic import View

from allauth.core.exceptions import ImmediateHttpResponse
from allauth.headless.internal.restkit.response import ErrorResponse


class RESTView(View):
    input_class = None
    handle_json_input = True

    def dispatch(self, request, *args, **kwargs):
        return self.handle(request, *args, **kwargs)

    def handle(self, request, *args, **kwargs):
        if self.handle_json_input and request.method != "GET":
            self.data = self._parse_json(request)
            response = self.handle_input(self.data)
            if response:
                return response
        return super().dispatch(request, *args, **kwargs)

    def get_input_kwargs(self):
        return {}

    def handle_input(self, data):
        input_class = self.input_class
        if isinstance(input_class, dict):
            input_class = input_class.get(self.request.method)
        if not input_class:
            return
        input_kwargs = self.get_input_kwargs()
        if data is None:
            # Make form bound on empty POST
            data = {}
        self.input = input_class(data=data, **input_kwargs)
        if not self.input.is_valid():
            return ErrorResponse(self.request, input=self.input)

    def _parse_json(self, request):
        if request.method == "GET" or not request.body:
            return
        try:
            return json.loads(request.body.decode("utf8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ImmediateHttpResponse(response=HttpResponseBadRequest())
