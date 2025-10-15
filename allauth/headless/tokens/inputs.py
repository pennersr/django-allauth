from allauth.headless.internal.restkit import inputs


class RefreshTokenInput(inputs.Input):
    refresh_token = inputs.CharField()
