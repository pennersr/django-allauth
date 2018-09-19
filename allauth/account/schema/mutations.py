import graphene
from . import input_types
from allauth.schema.types import UserType
from ..adapter import get_adapter
from allauth.account.utils import perform_login, app_settings


def _mutate_login(root, info, login_data, clazz):
    user = get_adapter(info.context).authenticate(
        info.context,
        username=login_data.username,
        password=login_data.password
    )
    if user:
        perform_login(info.context, user, email_verification=app_settings.EMAIL_VERIFICATION)
    return clazz(user=user)


class LoginUsername(graphene.Mutation):
    class Arguments:
        login_data = input_types.UsernameLoginInputType()

    user = graphene.Field(UserType)

    @staticmethod
    def mutate(*args, **kwargs):
        return _mutate_login(*args, clazz=LoginEmail, **kwargs)


class LoginEmail(graphene.Mutation):
    class Arguments:
        login_data = input_types.EmailLoginInputType()

    user = graphene.Field(UserType)

    @staticmethod
    def mutate(*args, **kwargs):
        return _mutate_login(*args, clazz=LoginEmail, **kwargs)


class Logout(graphene.Mutation):
    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, *args, **kwargs):
        get_adapter(info.context).logout(info.context)
        return Logout(ok=True)


class Mutation(object):
    login_email = LoginEmail.Field()
    login_username = LoginUsername.Field()
    logout = Logout.Field()
