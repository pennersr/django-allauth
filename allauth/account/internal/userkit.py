from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist


def user_id_to_str(user) -> str:
    return user._meta.pk.value_to_string(user)


def str_to_user_id(value: str):
    return get_user_model()._meta.pk.to_python(value)  # type: ignore[union-attr]


def user_field(user, field, *args, commit=False):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if not field:
        return
    User = get_user_model()
    try:
        field_meta = User._meta.get_field(field)
        max_length = field_meta.max_length
    except FieldDoesNotExist:
        if not hasattr(user, field):
            return
        max_length = None
    if args:
        # Setter
        v = args[0]
        if v:
            v = v[0:max_length]
        elif v is None and not field_meta.null:
            v = ""
        setattr(user, field, v)
        if commit:
            user.save(update_fields=[field])
    else:
        # Getter
        return getattr(user, field)
