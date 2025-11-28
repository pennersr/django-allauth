from django.conf import settings


PROVIDER_ID = "patreon"
API_VERSION = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("patreon", {})
    .get("VERSION", "v1")
)
USE_API_V2 = True if API_VERSION == "v2" else False
API_URL = f"https://www.patreon.com/api/oauth2/{API_VERSION if USE_API_V2 else 'api'}"
