from allauth.socialaccount.providers.discord_provider.provider import DiscordProvider
from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns


urlpatterns = default_urlpatterns(DiscordProvider)
