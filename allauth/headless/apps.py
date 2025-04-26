from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HeadlessConfig(AppConfig):
    name = "allauth.headless"
    verbose_name = _("Headless")

    def ready(self):
        from allauth.headless import checks  # noqa
