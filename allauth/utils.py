from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.core.validators import validate_email, ValidationError
from django.db.models import EmailField
from django.utils.http import urlencode
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils import importlib

import app_settings

def get_login_redirect_url(request, 
                           fallback=app_settings.LOGIN_REDIRECT_URL):
    """
    Returns a url to redirect to after the login
    """
    url = request.REQUEST.get(REDIRECT_FIELD_NAME) or fallback
    return url


def passthrough_login_redirect_url(request, url):
    assert url.find("?") < 0  # TODO: Handle this case properly
    next = get_login_redirect_url(request, fallback=None)
    if next:
        url = url + '?' + urlencode({ REDIRECT_FIELD_NAME: next })
    return url


def generate_unique_username(txt):
    username = slugify(txt.split('@')[0])
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
        users = User.objects
        if exclude_user:
            users = users.exclude(user=exclude_user)
        ret = users.filter(email__iexact=email).exists()
    return ret



def import_attribute(path):
    assert isinstance(path, str)
    pkg, attr = path.rsplit('.',1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret

def import_callable(path_or_callable):
    if not hasattr(path_or_callable, '__call__'):
        ret = import_attribute(path_or_callable)
    else:
        ret = path_or_callable
    return ret

