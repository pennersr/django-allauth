from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


def setup_dummy_social_apps(sender, **kwargs):
    """
    `allauth` needs tokens for OAuth based providers. So let's
    setup some dummy tokens
    """
    from django.contrib.sites.models import Site

    from allauth.socialaccount.models import SocialApp
    from allauth.socialaccount.providers import registry
    from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
    from allauth.socialaccount.providers.oauth.provider import OAuthProvider

    site = Site.objects.get_current()
    for provider_class in registry.get_class_list():
        if issubclass(provider_class, (OAuthProvider,OAuth2Provider)):
            try:
                SocialApp.objects.get(provider=provider_class.id, sites=site)
            except SocialApp.DoesNotExist:
                print(
                    "Installing dummy application credentials for %s."
                    " Authentication via this provider will not work"
                    " until you configure proper credentials via the"
                    " Django admin (`SocialApp` models)" % provider_class.id
                )
                app = SocialApp.objects.create(
                    provider=provider_class.id,
                    secret="secret",
                    client_id="client-id",
                    name="Dummy %s app" % provider_class.id,
                )
                app.sites.add(site)


class DemoConfig(AppConfig):
    name = "example.demo"
    verbose_name = _("Demo")
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        post_migrate.connect(setup_dummy_social_apps, sender=self)
