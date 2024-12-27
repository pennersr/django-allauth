import json

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View

from allauth.account.internal.decorators import login_not_required
from allauth.headless import app_settings
from allauth.headless.spec.internal.schema import get_schema


@method_decorator(login_not_required, name="dispatch")
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


@method_decorator(login_not_required, name="dispatch")
class OpenAPIJSONView(View):
    def get(self, request):
        spec = get_schema()
        content = json.dumps(spec)
        return HttpResponse(
            content,
            content_type="application/vnd.oai.openapi+json",
            headers={"Content-Disposition": "inline; filename=allauth-openapi.json"},
        )


@method_decorator(login_not_required, name="dispatch")
class OpenAPIHTMLView(TemplateView):
    def get_template_names(self):
        return [app_settings.SPECIFICATION_TEMPLATE_NAME]
