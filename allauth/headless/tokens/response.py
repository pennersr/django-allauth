from typing import Optional

from django.http import HttpRequest

from allauth.headless.base.response import APIResponse


class RefreshTokenResponse(APIResponse):
    def __init__(
        self, request: HttpRequest, access_token: str, refresh_token: Optional[str]
    ):
        data = {"access_token": access_token}
        if refresh_token:
            data["refresh_token"] = refresh_token
        super().__init__(request, data=data)
