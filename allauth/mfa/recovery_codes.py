import binascii
import hmac
import os
import struct
from hashlib import sha1

from allauth.mfa import app_settings
from allauth.mfa.models import Authenticator
from allauth.mfa.utils import decrypt, encrypt


class RecoveryCodes:
    def __init__(self, instance):
        self.instance = instance

    @classmethod
    def activate(cls, user):
        instance = Authenticator.objects.filter(
            user=user, type=Authenticator.Type.RECOVERY_CODES
        ).first()
        if instance:
            return cls(instance)
        instance = Authenticator(
            user=user,
            type=Authenticator.Type.RECOVERY_CODES,
            data={
                "seed": encrypt(cls.generate_seed()),
                "used_mask": 0,
            },
        )
        instance.save()
        return cls(instance)

    def generate_codes(self):
        ret = []
        seed = decrypt(self.instance.data["seed"])
        h = hmac.new(key=seed.encode("ascii"), msg=None, digestmod=sha1)
        for i in range(app_settings.RECOVERY_CODE_COUNT):
            h.update((f"{i:3},").encode("utf-8"))
            value = struct.unpack(">I", h.digest()[:4])[0]
            value %= 10**8
            fmt_value = f"{value:08}"
            ret.append(fmt_value)
        return ret

    def is_code_used(self, i):
        used_mask = self.instance.data["used_mask"]
        return bool(used_mask & (1 << i))

    def mark_code_used(self, i):
        used_mask = self.instance.data["used_mask"]
        used_mask |= 1 << i
        self.instance.data["used_mask"] = used_mask
        self.instance.save()

    def get_unused_codes(self):
        ret = []
        for i, code in enumerate(self.generate_codes()):
            if self.is_code_used(i):
                continue
            ret.append(code)
        return ret

    @classmethod
    def generate_seed(self):
        key = binascii.hexlify(os.urandom(20)).decode("ascii")
        return key

    def validate_code(self, code):
        for i, c in enumerate(self.generate_codes()):
            if self.is_code_used(i):
                continue
            if code == c:
                self.mark_code_used(i)
                return True
        return False
