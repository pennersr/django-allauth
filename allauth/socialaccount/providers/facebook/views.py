import logging
import requests

from django import forms
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.generic import View

from allauth.account.internal.decorators import login_not_required
from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.facebook import flows
from allauth.socialaccount.providers.facebook.constants import (
    GRAPH_API_URL,
    GRAPH_API_VERSION,
    PROVIDER_ID,
)
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .forms import FacebookConnectForm


logger = logging.getLogger(__name__)


class FacebookOAuth2Adapter(OAuth2Adapter):
    provider_id = PROVIDER_ID
    provider_default_auth_url = (
        f"https://www.facebook.com/{GRAPH_API_VERSION}/dialog/oauth"
    )

    settings = app_settings.PROVIDERS.get(provider_id, {})
    scope_delimiter = ","
    authorize_url = settings.get("AUTHORIZE_URL", provider_default_auth_url)
    access_token_url = f"{GRAPH_API_URL}/oauth/access_token"
    access_token_method = "GET"  # nosec
    expires_in_key = "expires_in"

    def complete_login(self, request, app, access_token, **kwargs):
        provider = self.get_provider()
        return flows.complete_login(request, provider, access_token)


oauth2_login = OAuth2LoginView.adapter_view(FacebookOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FacebookOAuth2Adapter)


class LoginByTokenView(View):
    @method_decorator(login_not_required)
    def dispatch(self, request):
        self.adapter = get_adapter()
        self.provider = self.adapter.get_provider(request, PROVIDER_ID)
        try:
            return super().dispatch(request)
        except (
            requests.RequestException,
            forms.ValidationError,
            PermissionDenied,
        ) as exc:
            return render_authentication_error(request, self.provider, exception=exc)

    def get(self, request):
        # If we leave out get().get() it will return a response with a 405, but
        # we really want to show an authentication error.
        raise PermissionDenied("405")

    def post(self, request):
        form = FacebookConnectForm(request.POST)
        if not form.is_valid():
            raise self.adapter.validation_error("invalid_token")
        access_token = form.cleaned_data["access_token"]
        provider = self.provider
        login_options = provider.get_fb_login_options(request)
        auth_type = login_options.get("auth_type")
        auth_nonce = ""
        if auth_type == "reauthenticate":
            auth_nonce = provider.get_nonce(request, pop=True)
        login = flows.verify_token(
            request, provider, access_token, auth_type, auth_nonce
        )
        login.state = SocialLogin.state_from_request(request)
        ret = complete_social_login(request, login)
        return ret


login_by_token = LoginByTokenView.as_view()
