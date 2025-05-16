from django.apps import AppConfig

from allauth import app_settings


class OIDCConfig(AppConfig):
    name = "allauth.idp.oidc"
    label = "allauth_idp_oidc"
    verbose_name = "OpenID Connect IdP"
    default_auto_field = (
        app_settings.DEFAULT_AUTO_FIELD or "django.db.models.BigAutoField"
    )
