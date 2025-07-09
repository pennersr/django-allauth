from typing import Optional

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models.fields import EmailField

from allauth.account.adapter import get_adapter


def valid_email_or_none(email: Optional[str]) -> Optional[str]:
    ret: Optional[str] = None
    try:
        if email:
            validate_email(email)
            max_length = EmailField().max_length
            if max_length is None or len(email) <= max_length:
                ret = get_adapter().clean_email(email.lower())
    except ValidationError:
        pass
    return ret
