import typing

from django.contrib import messages

from example.users.models import User

from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):

    def set_phone(self, user, phone: str, verified: bool):
        user.phone = phone
        user.phone_verified = verified
        user.save(update_fields=["phone", "phone_verified"])

    def get_phone(self, user) -> typing.Optional[typing.Tuple[str, bool]]:
        if user.phone:
            return user.phone, user.phone_verified
        return None

    def set_phone_verified(self, user, phone):
        self.set_phone(user, phone, True)

    def send_verification_code_sms(self, user, phone: str, code: str, **kwargs):
        messages.add_message(
            self.request,
            messages.WARNING,
            f"⚠️ SMS demo stub: assume code {code} was sent to {phone}.",
        )

    def send_unknown_account_sms(self, phone: str, **kwargs):
        messages.add_message(
            self.request,
            messages.WARNING,
            f"⚠️ SMS demo stub: Enumeration prevention: texted {phone} informing no account exists.",
        )

    def send_account_already_exists_sms(self, phone: str, **kwargs):
        messages.add_message(
            self.request,
            messages.WARNING,
            f"⚠️ SMS demo stub: Enumeration prevention: texted {phone} informing account already exists.",
        )

    def get_user_by_phone(self, phone):
        return User.objects.filter(phone=phone).order_by("-phone_verified").first()
