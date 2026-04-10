from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser

import fido2.features
from fido2.server import Fido2Server
from fido2.utils import websafe_decode
from fido2.webauthn import (
    AttestedCredentialData,
    AuthenticationResponse,
    AuthenticatorData,
    PublicKeyCredentialRpEntity,
    PublicKeyCredentialUserEntity,
    RegistrationResponse,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from allauth.account.utils import url_str_to_user_pk
from allauth.core import context
from allauth.mfa import app_settings
from allauth.mfa.adapter import get_adapter
from allauth.mfa.models import Authenticator


try:
    fido2.features.webauthn_json_mapping.enabled = True  # type:ignore[attr-defined]
except AttributeError:
    # https://github.com/Yubico/python-fido2/blob/main/doc/Migration_1-2.adoc
    pass

STATE_SESSION_KEY = "mfa.webauthn.state"
EXTENSIONS = {"credProps": True}


def build_user_payload(user: AbstractBaseUser) -> PublicKeyCredentialUserEntity:
    kwargs = get_adapter().get_public_key_credential_user_entity(user)
    return PublicKeyCredentialUserEntity(**kwargs)


def get_state() -> dict | None:
    return context.request.session.get(STATE_SESSION_KEY)


def set_state(state: dict) -> None:
    context.request.session[STATE_SESSION_KEY] = state


def clear_state() -> None:
    context.request.session.pop(STATE_SESSION_KEY, None)


def get_server() -> Fido2Server:
    rp_kwargs = get_adapter().get_public_key_credential_rp_entity()
    rp = PublicKeyCredentialRpEntity(**rp_kwargs)
    verify_origin = None
    if app_settings.WEBAUTHN_ALLOW_INSECURE_ORIGIN:
        verify_origin = lambda o: True  # noqa
    server = Fido2Server(rp, verify_origin=verify_origin)
    return server


def parse_registration_response(response: Any) -> RegistrationResponse:
    try:
        return RegistrationResponse.from_dict(response)
    except TypeError:
        raise get_adapter().validation_error("incorrect_code")


def begin_registration(user: AbstractBaseUser, passwordless: bool) -> dict:
    server = get_server()
    credentials = get_credentials(user)
    registration_data, state = server.register_begin(
        user=build_user_payload(user),
        credentials=credentials,
        resident_key_requirement=(
            ResidentKeyRequirement.REQUIRED
            if passwordless
            else ResidentKeyRequirement.DISCOURAGED
        ),
        user_verification=(
            UserVerificationRequirement.REQUIRED
            if passwordless
            else UserVerificationRequirement.DISCOURAGED
        ),
        extensions=EXTENSIONS,
    )
    set_state(state)
    return dict(registration_data)


def complete_registration(credential: dict) -> AuthenticatorData:
    server = get_server()
    state = get_state()
    if not state:
        raise get_adapter().validation_error("incorrect_code")
    try:
        binding = server.register_complete(state, credential)
    except ValueError:
        # raise ValueError("Wrong challenge in response.")
        raise get_adapter().validation_error("incorrect_code")
    clear_state()
    return binding


def get_credentials(user: AbstractBaseUser) -> list[AttestedCredentialData]:
    credentials: list[AttestedCredentialData] = []
    authenticators = Authenticator.objects.filter(
        user_id=user.pk, type=Authenticator.Type.WEBAUTHN
    )
    for authenticator in authenticators:
        credential_data = authenticator.wrap().authenticator_data.credential_data
        if credential_data:
            credentials.append(authenticator.wrap().authenticator_data.credential_data)
    return credentials


def get_authenticator_by_credential_id(
    user: AbstractBaseUser, credential_id: bytes
) -> Authenticator | None:
    authenticators = Authenticator.objects.filter(
        user_id=user.pk, type=Authenticator.Type.WEBAUTHN
    )
    for authenticator in authenticators:
        if (
            credential_id
            == authenticator.wrap().authenticator_data.credential_data.credential_id
        ):
            return authenticator
    return None


def parse_authentication_response(response: Any) -> AuthenticationResponse:
    try:
        return AuthenticationResponse.from_dict(response)
    except (TypeError, ValueError):
        raise get_adapter().validation_error("incorrect_code")


def begin_authentication(user: AbstractBaseUser | None = None) -> dict:
    server = get_server()
    request_options, state = server.authenticate_begin(
        credentials=get_credentials(user) if user else [],
        user_verification=UserVerificationRequirement.PREFERRED,
    )
    set_state(state)
    return dict(request_options)


def extract_user_from_response(response: dict) -> AbstractBaseUser:
    try:
        user_handle = response.get("response", {}).get("userHandle")
        user_pk = url_str_to_user_pk(websafe_decode(user_handle).decode("utf8"))
    except (ValueError, TypeError, KeyError):
        raise get_adapter().validation_error("incorrect_code")
    user = get_user_model().objects.filter(pk=user_pk).first()
    if not user:
        raise get_adapter().validation_error("incorrect_code")
    return user


def complete_authentication(user: AbstractBaseUser, response: dict) -> Authenticator:
    credentials = get_credentials(user)
    server = get_server()
    state = get_state()
    if not state:
        raise get_adapter().validation_error("incorrect_code")
    try:
        binding = server.authenticate_complete(state, credentials, response)
    except ValueError as e:
        # ValueError: Unknown credential ID.
        raise get_adapter().validation_error("incorrect_code") from e
    clear_state()
    authenticator = get_authenticator_by_credential_id(user, binding.credential_id)
    if not authenticator:
        raise get_adapter().validation_error("incorrect_code")
    return authenticator


class WebAuthn:
    def __init__(self, instance) -> None:
        self.instance = instance

    @classmethod
    def add(cls, user: AbstractBaseUser, name: str, credential: dict) -> "WebAuthn":
        instance = Authenticator(
            user=user,  # type:ignore[misc]
            type=Authenticator.Type.WEBAUTHN,
            data={
                "name": name,
                "credential": credential,
            },
        )
        instance.save()
        return cls(instance)

    @property
    def name(self) -> str:
        return self.instance.data["name"]

    @name.setter
    def name(self, name: str) -> None:
        self.instance.data["name"] = name

    @property
    def authenticator_data(self) -> AuthenticatorData:
        return parse_registration_response(
            self.instance.data["credential"]
        ).response.attestation_object.auth_data

    @property
    def is_passwordless(self) -> bool | None:
        return (
            self.instance.data.get("credential", {})
            .get("clientExtensionResults", {})
            .get("credProps", {})
            .get("rk")
        )
