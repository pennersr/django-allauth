import json

from django.http import HttpResponse
from django.views.generic import TemplateView, View

from allauth.headless.spec.internal.schema import get_schema


class OpenAPIYAMLView(View):
    def get(self, request):
        import yaml

        spec = get_schema()
        content = yaml.dump(spec, Dumper=yaml.Dumper)
        return HttpResponse(
            content,
            content_type="application/vnd.oai.openapi",
            headers={"Content-Disposition": "inline; filename=allauth-openapi.yaml"},
        )


class OpenAPIJSONView(View):
    def get(self, request):
        spec = get_schema()
        content = json.dumps(spec)
        return HttpResponse(
            content,
            content_type="application/vnd.oai.openapi+json",
            headers={"Content-Disposition": "inline; filename=allauth-openapi.json"},
        )


class OpenAPIDocumentationView(TemplateView):
    template_name = "headless/openapi.html"
