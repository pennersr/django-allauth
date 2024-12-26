import json

from django.http import HttpResponse
from django.views.generic import TemplateView, View

from allauth.headless import app_settings
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


class OpenAPIHTMLView(TemplateView):
    def get_template_names(self):
        return [app_settings.SPECIFICATION_TEMPLATE_NAME]
