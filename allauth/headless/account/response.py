from __future__ import annotations

from http import HTTPStatus

from allauth.headless.adapter import get_adapter
from allauth.headless.base.response import APIResponse


def email_address_data(addr) -> dict:
    return {
        "email": addr.email,
        "verified": addr.verified,
        "primary": addr.primary,
    }


class RequestEmailVerificationResponse(APIResponse):
    def __init__(self, request, verification_sent) -> None:
        super().__init__(
            request, status=HTTPStatus.OK if verification_sent else HTTPStatus.FORBIDDEN
        )


class VerifyEmailResponse(APIResponse):
    def __init__(self, request, email_address, stage) -> None:
        adapter = get_adapter()
        data = {
            "email": email_address.email,
            "user": adapter.serialize_user(email_address.user),
        }
        meta = {
            "is_authenticating": stage is not None,
        }
        super().__init__(request, data=data, meta=meta)


class EmailAddressesResponse(APIResponse):
    def __init__(self, request, email_addresses) -> None:
        data = [email_address_data(addr) for addr in email_addresses]
        super().__init__(request, data=data)


class PhoneNumbersResponse(APIResponse):
    def __init__(self, request, phone_numbers, status=HTTPStatus.OK) -> None:
        super().__init__(request, data=phone_numbers, status=status)


class RequestPasswordResponse(APIResponse):
    pass


class PasswordResetKeyResponse(APIResponse):
    def __init__(self, request, user) -> None:
        adapter = get_adapter()
        data = {"user": adapter.serialize_user(user)}
        super().__init__(request, data=data)
