import typing

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from allauth.account.adapter import DefaultAccountAdapter
from tests.projects.common import phone_stub


messagesoutbox = []


class AccountAdapter(DefaultAccountAdapter):
    def set_phone(self, user, phone: str, verified: bool):
        phone_stub.set_phone(user.pk, phone, verified)

    def get_phone(self, user) -> typing.Optional[typing.Tuple[str, bool]]:
        return phone_stub.get_phone(user.pk)

    def set_phone_verified(self, user, phone: str):
        phone_stub.set_phone(user.pk, phone, True)

    def get_user_by_phone(self, phone):
        user_id = phone_stub.get_user_id_by_phone(phone)
        if user_id is None:
            return None
        User = get_user_model()
        return User.objects.filter(pk=user_id).first()

    def send_verification_code_sms(self, user, phone: str, code: str, **kwargs):
        phone_stub.send_verification_code_sms(user, phone, code)

    def send_unknown_account_sms(self, phone: str, **kwargs: typing.Any) -> None:
        phone_stub.send_unknown_account_sms(phone)

    def send_account_already_exists_sms(self, phone: str, **kwargs: typing.Any) -> None:
        phone_stub.send_account_already_exists_sms(phone)

    def add_message(self, *args, **kwargs):
        message_template = kwargs.get("message_template")
        message = None
        if message_template is None:
            message = kwargs.get("message")
            if message is None:
                message_template = args[2]
        messagesoutbox.append(dict(message=message, message_template=message_template))
        return super().add_message(*args, **kwargs)

    def clean_email(self, email):
        if email == "invalid@test.email":
            raise ValidationError("testing")
        return email
