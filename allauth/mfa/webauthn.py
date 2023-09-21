import base64
import json
import os
from typing import Mapping

from fido2.server import Fido2Server
from fido2.utils import websafe_decode, websafe_encode
from fido2.webauthn import (
    AttestationObject,
    AuthenticatorData,
    CollectedClientData,
    PublicKeyCredentialRpEntity,
)

from allauth.core import context
from allauth.mfa import app_settings
from allauth.mfa.models import Authenticator


CHALLENGE_SESSION_KEY = "mfa.webauthn.challenge"
STATE_SESSION_KEY = "mfa.webauthn.state"


class B64JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Mapping):
            return {k: v for k, v in obj.items()}
        elif isinstance(obj, bytes):
            return base64.b64encode(obj).decode("ascii")
        return super().default(obj)


def b64_json_dumps(data):
    return json.dumps(data, cls=B64JSONEncoder)


def parse_authentication_credential(credential):
    response = credential["response"]
    client_data = parse_client_data_json(response["clientDataJSON"])
    return {
        "credential_id": websafe_decode(credential["id"]),
        "signature": base64.b64decode(response["signature"]),
        "auth_data": AuthenticatorData(base64.b64decode(response["authenticatorData"])),
        "client_data": client_data,
    }


def parse_client_data_json(text):
    client_data = CollectedClientData(base64.b64decode(text))

    if app_settings.WEBAUTHN_ALLOW_INSECURE_ORIGIN:
        # fido2.rpid.verify_rp_id() enforces "https", which is problematic when testing
        # with a localhost runserver. So, here we fake a HTTPS origin.
        #
        # WARNING! Only use for local development purposes.
        class CollectedClientDataWithFakeSecureOrigin:
            def __getattribute__(self, name):
                if name == "origin":
                    return client_data.origin.replace("http://", "https://")
                return getattr(client_data, name)

        return CollectedClientDataWithFakeSecureOrigin()
    return client_data


def parse_attestation_object(text):
    return AttestationObject(base64.b64decode(text))


def generate_challenge() -> bytes:
    challenge = context.request.session.get(CHALLENGE_SESSION_KEY)
    if challenge is not None:
        return websafe_decode(challenge)
    challenge = os.urandom(32)
    context.request.session[CHALLENGE_SESSION_KEY] = websafe_encode(challenge)
    return challenge


def consume_challenge():
    context.request.session.pop(CHALLENGE_SESSION_KEY, None)


def get_state():
    return context.request.session.get(STATE_SESSION_KEY)


def set_state(state):
    context.request.session[STATE_SESSION_KEY] = state


def clear_state():
    context.request.session.pop(STATE_SESSION_KEY, None)


def get_server():
    rp_id = "localhost"
    rp = PublicKeyCredentialRpEntity("allauth", rp_id)
    server = Fido2Server(rp)
    return server


def begin_registration():
    server = get_server()
    credentials = []
    registration_data, state = server.register_begin(
        user={
            "id": b"123",
            "name": "name",
            "displayName": "Displayname",
        },
        credentials=credentials,
        user_verification="discouraged",
        challenge=generate_challenge(),
    )
    set_state(state)
    registration_data = json.loads(b64_json_dumps(registration_data))
    return registration_data


def parse_registration_credential(credential):
    response = credential["response"]
    attestation_object = parse_attestation_object(response["attestationObject"])
    client_data = parse_client_data_json(response["clientDataJSON"])
    return {"client_data": client_data, "attestation_object": attestation_object}


def complete_registration(credential):
    server = get_server()
    state = get_state()
    binding = server.register_complete(
        state, credential["client_data"], credential["attestation_object"]
    )
    consume_challenge()
    clear_state()
    return base64.b64encode(bytes(binding)).decode("ascii")


def get_credentials(user):
    credentials = []
    authenticators = Authenticator.objects.filter(type=Authenticator.Type.WEBAUTHN)
    for authenticator in authenticators:
        credentials.append(authenticator.wrap().authenticator_data.credential_data)
    return credentials


def begin_authentication(user):
    server = get_server()
    request_options, state = server.authenticate_begin(
        credentials=get_credentials(user), user_verification="discouraged"
    )
    set_state(state)
    request_options = json.loads(b64_json_dumps(request_options))
    return request_options


def complete_authentication(state, credentials, public_key_credential):
    server = get_server()
    state = get_state()
    binding = server.authenticate_complete(state, credentials, **public_key_credential)
    # ValueError: Unknown credential ID.
    consume_challenge()
    clear_state()
    return base64.b64encode(bytes(binding)).decode("ascii")


class WebAuthn:
    def __init__(self, instance):
        self.instance = instance

    @classmethod
    def add(cls, user, authenticator_data):
        instance = Authenticator(
            user=user,
            type=Authenticator.Type.WEBAUTHN,
            data={"authenticator_data": authenticator_data},
        )
        instance.save()
        return cls(instance)

    @property
    def authenticator_data(self):
        return AuthenticatorData(
            base64.b64decode(self.instance.data["authenticator_data"])
        )