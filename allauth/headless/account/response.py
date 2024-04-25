from allauth.headless.base.response import APIResponse, user_data


class RequestEmailVerificationResponse(APIResponse):
    def __init__(self, request, verification_sent):
        super().__init__(request, status=200 if verification_sent else 403)


class VerifyEmailResponse(APIResponse):
    def __init__(self, request, verification, stage):
        data = {
            "email": verification.email_address.email,
            "user": user_data(verification.email_address.user),
        }
        meta = {
            "is_authenticating": stage is not None,
        }
        super().__init__(request, data=data, meta=meta)


class EmailAddressesResponse(APIResponse):
    def __init__(self, request, email_addresses):
        data = [
            {
                "email": addr.email,
                "verified": addr.verified,
                "primary": addr.primary,
            }
            for addr in email_addresses
        ]
        super().__init__(request, data=data)


class RequestPasswordResponse(APIResponse):
    pass


class PasswordResetKeyResponse(APIResponse):
    def __init__(self, request, user):
        data = {"user": user_data(user)}
        super().__init__(request, data=data)
