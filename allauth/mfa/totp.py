import base64
import hashlib
import hmac
import secrets
import struct
import time
from io import BytesIO
from urllib.parse import quote

from django.core.cache import cache
from django.utils.http import urlencode

import qrcode
from qrcode.image.svg import SvgPathImage

from allauth.core import context
from allauth.mfa import app_settings
from allauth.mfa.models import Authenticator
from allauth.mfa.utils import decrypt, encrypt


SECRET_SESSION_KEY = "mfa.totp.secret"


def generate_totp_secret(length=20):
    random_bytes = secrets.token_bytes(length)
    return base64.b32encode(random_bytes).decode("utf-8")


def get_totp_secret(regenerate=False):
    secret = None
    if not regenerate:
        secret = context.request.session.get(SECRET_SESSION_KEY)
    if not secret:
        secret = context.request.session[SECRET_SESSION_KEY] = generate_totp_secret()
    return secret


def hotp_counter_from_time():
    current_time = int(time.time())  # Get the current Unix timestamp
    return current_time // app_settings.TOTP_PERIOD


def hotp_value(secret, counter):
    # Convert the counter to a byte array using big-endian encoding
    counter_bytes = struct.pack(">Q", counter)
    secret_enc = base64.b32decode(secret.encode("ascii"), casefold=True)
    # Calculate the HMAC-SHA1 hash using the secret and counter
    hmac_result = hmac.new(secret_enc, counter_bytes, hashlib.sha1).digest()
    # Get the last 4 bits of the HMAC result to determine the offset
    offset = hmac_result[-1] & 0x0F
    # Extract an 31-bit slice from the HMAC result starting at the offset + 1 bit
    truncated_hash = bytearray(hmac_result[offset : offset + 4])
    truncated_hash[0] = truncated_hash[0] & 0x7F
    # Convert the truncated hash to an integer value
    value = struct.unpack(">I", truncated_hash)[0]
    # Apply modulo to get a value within the specified number of digits
    value %= 10**app_settings.TOTP_DIGITS
    return value


def build_totp_url(label, issuer, secret):
    params = {
        "secret": secret,
        # This is the default
        # "algorithm": "SHA1",
        "issuer": issuer,
    }
    if app_settings.TOTP_DIGITS != 6:
        params["digits"] = app_settings.TOTP_DIGITS
    if app_settings.TOTP_PERIOD != 30:
        params["period"] = app_settings.TOTP_PERIOD
    return f"otpauth://totp/{quote(label)}?{urlencode(params)}"


def build_totp_svg(url):
    img = qrcode.make(url, image_factory=SvgPathImage)
    buf = BytesIO()
    img.save(buf)
    return buf.getvalue().decode("utf8")


def format_hotp_value(value):
    return f"{value:0{app_settings.TOTP_DIGITS}}"


def validate_totp_code(secret, code):
    value = hotp_value(secret, hotp_counter_from_time())
    return code == format_hotp_value(value)


class TOTP:
    def __init__(self, instance):
        self.instance = instance

    @classmethod
    def activate(cls, user, secret):
        instance = Authenticator(
            user=user, type=Authenticator.Type.TOTP, data={"secret": encrypt(secret)}
        )
        instance.save()
        return cls(instance)

    def deactivate(self):
        self.instance.delete()

    def validate_code(self, code):
        if self._is_code_used(code):
            return False

        secret = decrypt(self.instance.data["secret"])
        valid = validate_totp_code(secret, code)
        if valid:
            self._mark_code_used(code)
        return valid

    def _get_used_cache_key(self, code):
        return f"allauth.mfa.totp.used?user={self.instance.user_id}&code={code}"

    def _is_code_used(self, code):
        return cache.get(self._get_used_cache_key(code)) == "y"

    def _mark_code_used(self, code):
        cache.set(self._get_used_cache_key(code), "y", timeout=app_settings.TOTP_PERIOD)
