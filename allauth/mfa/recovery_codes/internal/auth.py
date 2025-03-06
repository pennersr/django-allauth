import hmac
import secrets
from hashlib import sha1
from typing import List, Optional

from allauth.mfa import app_settings
from allauth.mfa.models import Authenticator
from allauth.mfa.utils import decrypt, encrypt


class RecoveryCodes:
    def __init__(self, instance: Authenticator) -> None:
        self.instance = instance

    @classmethod
    def activate(cls, user) -> "RecoveryCodes":
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

    @classmethod
    def generate_seed(self) -> str:
        key = secrets.token_hex(40)
        return key

    def _get_migrated_codes(self) -> Optional[List[str]]:
        codes = self.instance.data.get("migrated_codes")
        if codes is not None:
            return [decrypt(code) for code in codes]
        return None

    def generate_codes(self) -> List[str]:
        migrated_codes = self._get_migrated_codes()
        if migrated_codes is not None:
            return migrated_codes

        ret = []
        seed = decrypt(self.instance.data["seed"])
        h = hmac.new(key=seed.encode("ascii"), msg=None, digestmod=sha1)
        byte_count = min(app_settings.RECOVERY_CODE_DIGITS // 2, h.digest_size)
        for i in range(app_settings.RECOVERY_CODE_COUNT):
            h.update((f"{i:3},").encode("utf-8"))
            value = int.from_bytes(
                h.digest()[:byte_count], byteorder="big", signed=False
            )
            value %= 10**app_settings.RECOVERY_CODE_DIGITS
            fmt_value = str(value).zfill(app_settings.RECOVERY_CODE_DIGITS)
            ret.append(fmt_value)
        return ret

    def _is_code_used(self, i: int) -> bool:
        used_mask = self.instance.data["used_mask"]
        return bool(used_mask & (1 << i))

    def _mark_code_used(self, i: int) -> None:
        used_mask = self.instance.data["used_mask"]
        used_mask |= 1 << i
        self.instance.data["used_mask"] = used_mask
        self.instance.save()

    def get_unused_codes(self) -> List[str]:
        migrated_codes = self._get_migrated_codes()
        if migrated_codes is not None:
            return migrated_codes

        ret = []
        for i, code in enumerate(self.generate_codes()):
            if self._is_code_used(i):
                continue
            ret.append(code)
        return ret

    def _validate_migrated_code(self, code: str) -> Optional[bool]:
        migrated_codes = self._get_migrated_codes()
        if migrated_codes is None:
            return None
        try:
            idx = migrated_codes.index(code)
        except ValueError:
            return False
        else:
            migrated_codes = self.instance.data["migrated_codes"]
            assert isinstance(migrated_codes, list)  # nosec
            migrated_codes.pop(idx)
            self.instance.data["migrated_codes"] = migrated_codes
            self.instance.save()
            return True

    def validate_code(self, code: str) -> bool:
        ret = self._validate_migrated_code(code)
        if ret is not None:
            return ret

        for i, c in enumerate(self.generate_codes()):
            if self._is_code_used(i):
                continue
            if code == c:
                self._mark_code_used(i)
                return True
        return False
