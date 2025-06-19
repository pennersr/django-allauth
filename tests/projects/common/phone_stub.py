import typing

from django.db.utils import IntegrityError


db: typing.Dict[int, typing.Tuple[str, bool]] = {}
sms_outbox: typing.List[typing.Dict] = []


def clear():
    global db
    db.clear()
    sms_outbox.clear()


def set_phone(user_id, phone: str, verified: bool):
    for other_user_id, value in db.items():
        if user_id != other_user_id and value[0] == phone:
            raise IntegrityError
    db[user_id] = (phone, verified)


def get_phone(user_id) -> typing.Optional[typing.Tuple[str, bool]]:
    return db.get(user_id)


def send_verification_code_sms(user, phone: str, code: str):
    sms_outbox.append(
        {
            "user_id": user.pk,
            "phone": phone,
            "code": code,
        }
    )


def send_unknown_account_sms(phone: str, **kwargs: typing.Any):
    sms_outbox.append({"phone": phone, "reason": "unknon"})


def send_account_already_exists_sms(phone: str, **kwargs: typing.Any):
    sms_outbox.append({"phone": phone, "reason": "exists"})


def get_user_id_by_phone(phone):
    for k, v in db.items():
        if v[0] == phone:
            return k
    return None
