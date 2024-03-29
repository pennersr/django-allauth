from django.conf import settings


_FXA_SETTINGS = getattr(settings, "SOCIALACCOUNT_PROVIDERS", {}).get("fxa", {})
FXA_OAUTH_ENDPOINT = _FXA_SETTINGS.get(
    "OAUTH_ENDPOINT", "https://oauth.accounts.firefox.com/v1"
)
FXA_PROFILE_ENDPOINT = _FXA_SETTINGS.get(
    "PROFILE_ENDPOINT", "https://profile.accounts.firefox.com/v1"
)
PROVIDER_ID = "fxa"
