from django.core.checks import Critical, register


@register()
def settings_check(app_configs, **kwargs):
    from allauth.headless import app_settings

    ret = []
    if app_settings.SERVE_SPECIFICATION:
        try:
            import yaml  # noqa
        except ImportError:
            ret.append(
                Critical(
                    msg="HEADLESS_SERVE_SPECIFICATION requires the django-allauth[headless-spec] extra to be installed"
                )
            )
    return ret
