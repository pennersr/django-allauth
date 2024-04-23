from django.conf import settings


PROVIDER_ID = "facebook"
GRAPH_API_VERSION = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("facebook", {})
    .get("VERSION", "v19.0")
)
GRAPH_API_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("facebook", {})
    .get("GRAPH_API_URL", "https://graph.facebook.com/{}".format(GRAPH_API_VERSION))
)

NONCE_SESSION_KEY = "allauth_facebook_nonce"
NONCE_LENGTH = 32
