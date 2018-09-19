from graphene_django.types import DjangoObjectType
from .. import models


class EmailConfirmationType(DjangoObjectType):
    class Meta:
        model = models.EmailConfirmation


class EmailAddressType(DjangoObjectType):
    class Meta:
        model = models.EmailAddress
