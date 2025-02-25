import typing

from django.contrib.auth import get_user_model

from allauth.account.adapter import DefaultAccountAdapter
from tests.common import phone_stub


class AccountAdapter(DefaultAccountAdapter):
    def set_phone(self, user, phone: str, verified: bool):
        phone_stub.set_phone(user.pk, phone, verified)

    def get_phone(self, user) -> typing.Optional[typing.Tuple[str, bool]]:
        return phone_stub.get_phone(user.pk)

    def set_phone_verified(self, user, phone: str):
        phone_stub.set_phone(user.pk, phone, True)

    def get_user_by_phone(self, phone):
        user_id = phone_stub.get_user_id_by_phone(phone)
        User = get_user_model()
        return User.objects.filter(pk=user_id).first()

    def send_phone_verification_code(self, *, user, phone: str, code: str, **kwargs):
        phone_stub.send_phone_verification_code(user, phone, code)
