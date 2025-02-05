from django.apps import AppConfig, apps
from django.test import TestCase
from django.test.utils import override_settings

from allauth.socialaccount import providers


class CustomFacebookAppConfig(AppConfig):
    name = "allauth.socialaccount.providers.facebook"
    label = "allauth_facebook"


class ProviderRegistryTests(TestCase):
    @override_settings(
        INSTALLED_APPS=[
            "allauth.socialaccount.providers.facebook",
        ]
    )
    def test_load_provider_with_default_app_config(self):
        registry = providers.ProviderRegistry()
        provider_list = registry.get_class_list()

        self.assertTrue(registry.loaded)
        self.assertEqual(1, len(provider_list))
        self.assertTrue(
            issubclass(
                provider_list[0],
                providers.facebook.provider.FacebookProvider,
            )
        )

        app_config_list = list(apps.get_app_configs())
        self.assertEqual(1, len(app_config_list))
        app_config = app_config_list[0]
        self.assertEqual("allauth.socialaccount.providers.facebook", app_config.name)
        self.assertEqual("facebook", app_config.label)

    @override_settings(
        INSTALLED_APPS=[
            "allauth.socialaccount.tests.test_registry.CustomFacebookAppConfig",
        ]
    )
    def test_load_provider_with_custom_app_config(self):
        registry = providers.ProviderRegistry()
        provider_list = registry.get_class_list()

        self.assertTrue(registry.loaded)
        self.assertEqual(1, len(provider_list))
        self.assertTrue(
            issubclass(
                provider_list[0],
                providers.facebook.provider.FacebookProvider,
            )
        )

        app_config_list = list(apps.get_app_configs())
        self.assertEqual(1, len(app_config_list))
        app_config = app_config_list[0]
        self.assertEqual("allauth.socialaccount.providers.facebook", app_config.name)
        self.assertEqual("allauth_facebook", app_config.label)
