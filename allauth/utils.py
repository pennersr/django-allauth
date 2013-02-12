import re
import unicodedata

from django.core.exceptions import ImproperlyConfigured
from django.core.validators import validate_email, ValidationError
from django.db.models import EmailField
from django.utils.http import urlencode
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils import importlib

import app_settings

def get_login_redirect_url(request, 
                           fallback=True):
    """
    Returns a url to redirect to after the login
    
    TODO: 
    - Cleanup, check overlap with account.utils.get_default_redirect
    - Move to allauth.account
    """
    if fallback and type(fallback) == bool:
        from account.adapter import get_adapter
        fallback = get_adapter().get_login_redirect_url(request)
    url = request.REQUEST.get(REDIRECT_FIELD_NAME) or fallback
    return url


def passthrough_login_redirect_url(request, url):
    assert url.find("?") < 0  # TODO: Handle this case properly
    next = get_login_redirect_url(request, fallback=None)
    if next:
        url = url + '?' + urlencode({ REDIRECT_FIELD_NAME: next })
    return url


def generate_unique_username(txt):
    username = unicodedata.normalize('NFKD', unicode(txt))
    username = username.encode('ascii', 'ignore')
    username = unicode(re.sub('[^\w\s@+.-]', '', username).lower())
    # Django allows for '@' in usernames in order to accomodate for
    # project wanting to use e-mail for username. In allauth we don't
    # use this, we already have a proper place for putting e-mail
    # addresses (EmailAddress), so let's not use the full e-mail
    # address and only take the part leading up to the '@'.
    username = username.split('@')[0]
    username = username.strip() or 'user'
    User = get_user_model()
    max_length = User._meta.get_field('username').max_length
    i = 0
    while True:
        try:
            if i:
                pfx = str(i + 1)
            else:
                pfx = ''
            ret = username[0:max_length - len(pfx)] + pfx
            User.objects.get(username=ret)
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
    from allauth.account.models import EmailAddress

    emailaddresses = EmailAddress.objects
    if exclude_user:
        emailaddresses = emailaddresses.exclude(user=exclude_user)
    ret = emailaddresses.filter(email__iexact=email).exists()
    if not ret:
        users = get_user_model().objects
        if exclude_user:
            users = users.exclude(pk=exclude_user.pk)
        ret = users.filter(email__iexact=email).exists()
    return ret



def import_attribute(path):
    assert isinstance(path, basestring)
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

    
