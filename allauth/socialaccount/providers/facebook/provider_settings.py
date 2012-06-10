from django.conf import settings

# Locale to use for the Facebook Javascript SDK
# List available at https://www.facebook.com/translations/FacebookLocales.xml
JSSDK_LOCALE = getattr(settings, "SOCIALACCOUNT_FACEBOOK_JSSDK_LOCALE", "en_US")
