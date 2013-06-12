import re
import unicodedata

from django.core.exceptions import ImproperlyConfigured
from django.core.validators import validate_email, ValidationError
from django.core import urlresolvers
from django.db.models import EmailField, FieldDoesNotExist
from django.utils import importlib, six
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

from . import app_settings


def generate_unique_username(txt):
    from .account.app_settings import USER_MODEL_USERNAME_FIELD

    username = unicodedata.normalize('NFKD', force_text(txt))
    username = username.encode('ascii', 'ignore').decode('ascii')
    username = force_text(re.sub('[^\w\s@+.-]', '', username).lower())
    # Django allows for '@' in usernames in order to accomodate for
    # project wanting to use e-mail for username. In allauth we don't
    # use this, we already have a proper place for putting e-mail
    # addresses (EmailAddress), so let's not use the full e-mail
    # address and only take the part leading up to the '@'.
    username = username.split('@')[0]
    username = username.strip() or 'user'

    User = get_user_model()
    try:
        max_length = User._meta.get_field(USER_MODEL_USERNAME_FIELD).max_length
    except FieldDoesNotExist:
        raise ImproperlyConfigured(
            "USER_MODEL_USERNAME_FIELD does not exist in user-model"
        )
    i = 0
    while True:
        try:
            if i:
                pfx = str(i + 1)
            else:
                pfx = ''
            ret = username[0:max_length - len(pfx)] + pfx
            User.objects.get(**{USER_MODEL_USERNAME_FIELD: ret})
            i += 1
        except User.DoesNotExist:
            return ret


def valid_email_or_none(email):
    ret = None
    try:
        if email:
            validate_email(email)
            if len(email) <= EmailField().max_length:
                ret = email
    except ValidationError:
        pass
    return ret


def email_address_exists(email, exclude_user=None):
    from .account import app_settings as account_settings
    from .account.models import EmailAddress

    emailaddresses = EmailAddress.objects
    if exclude_user:
        emailaddresses = emailaddresses.exclude(user=exclude_user)
    ret = emailaddresses.filter(email__iexact=email).exists()
    if not ret:
        email_field = account_settings.USER_MODEL_EMAIL_FIELD
        if email_field:
            users = get_user_model().objects
            if exclude_user:
                users = users.exclude(pk=exclude_user.pk)
            ret = users.filter(**{email_field+'__iexact': email}).exists()
    return ret



def import_attribute(path):
    assert isinstance(path, six.string_types)
    pkg, attr = path.rsplit('.',1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret

def import_callable(path_or_callable):
    if not hasattr(path_or_callable, '__call__'):
        ret = import_attribute(path_or_callable)
    else:
        ret = path_or_callable
    return ret


def get_user_model():
    from django.db.models import get_model

    try:
        app_label, model_name = app_settings.USER_MODEL.split('.')
    except ValueError:
        raise ImproperlyConfigured("AUTH_USER_MODEL must be of the form 'app_label.model_name'")
    user_model = get_model(app_label, model_name)
    if user_model is None:
        raise ImproperlyConfigured("AUTH_USER_MODEL refers to model '%s' that has not been installed" % app_settings.USER_MODEL)
    return user_model

def resolve_url(to):
    """
    Subset of django.shortcuts.resolve_url (that one is 1.5+)
    """
    try:
        return urlresolvers.reverse(to)
    except urlresolvers.NoReverseMatch:
        # If this doesn't "feel" like a URL, re-raise.
        if '/' not in to and '.' not in to:
            raise
    # Finally, fall back and assume it's a URL
    return to
