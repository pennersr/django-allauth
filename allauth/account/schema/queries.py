import graphene
from . import types
from .. import models
from django.core.exceptions import PermissionDenied


def login_required(func):
    def wrapper(*args, **kwargs):
        if not args[1].context.user.is_authenticated:
            raise PermissionDenied("Unauthorized")
        return func(*args, **kwargs)
    return wrapper


class Query(object):
    user_email_addresses = graphene.List(types.EmailAddressType)

    @login_required
    def resolve_user_email_addresses(self, info, **kwargs):
        return models.EmailAddress.objects.filter(user=info.context.user)
