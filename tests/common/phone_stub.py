import typing


db: typing.Dict[int, typing.Tuple[str, bool]] = {}
sms_outbox: typing.List[typing.Dict] = []


def clear():
    global db
    db.clear()
    sms_outbox.clear()


def set_phone(user_id, phone: str, verified: bool):
    db[user_id] = (phone, verified)


def get_phone(user_id) -> typing.Optional[typing.Tuple[str, bool]]:
    return db.get(user_id)


def send_phone_verification_code(user, phone: str, code: str, signup: bool):
    sms_outbox.append(
        {
            "user_id": user.pk,
            "phone": phone,
            "code": code,
            "signup": signup,
        }
    )


def get_user_id_by_phone(phone):
    for k, v in db.items():
        if v[0] == phone:
            return k
    return None
