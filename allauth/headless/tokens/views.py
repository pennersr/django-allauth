from typing import Optional

from django.http import HttpRequest

from allauth.headless import app_settings
from allauth.headless.base.views import APIView
from allauth.headless.internal.restkit.response import ErrorResponse
from allauth.headless.tokens.inputs import RefreshTokenInput
from allauth.headless.tokens.response import RefreshTokenResponse
from allauth.headless.tokens.strategies.base import AbstractTokenStrategy


class RefreshTokenView(APIView):
    input_class = RefreshTokenInput

    def post(self, request: HttpRequest):
        refresh_token = self.input.cleaned_data["refresh_token"]
        strategy: AbstractTokenStrategy = app_settings.TOKEN_STRATEGY
        at_rt = strategy.refresh_token(refresh_token)
        if at_rt is None:
            return ErrorResponse(request)

        next_refresh_token: Optional[str]
        access_token, next_refresh_token = at_rt
        if next_refresh_token == refresh_token:
            next_refresh_token = None
        return RefreshTokenResponse(request, access_token, next_refresh_token)
