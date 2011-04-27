import app_settings

def allauth(request):
    ctx = dict(facebook_enabled=app_settings.FACEBOOK_ENABLED,
               twitter_enabled=app_settings.TWITTER_ENABLED,
               openid_enabled=app_settings.OPENID_ENABLED,
               socialaccount_enabled=app_settings.SOCIALACCOUNT_ENABLED)
    return dict(allauth=ctx)
