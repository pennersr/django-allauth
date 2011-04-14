from django.conf import settings
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.core.validators import validate_email, ValidationError
from django.db.models import EmailField
from django.utils.http import urlencode

from emailconfirmation.models import EmailAddress

def get_login_redirect_url(request):
    """
    Returns a url to redirect to after the login
    """
    next = None
    if 'next' in request.session:
        next = request.session['next']
        del request.session['next']
    elif 'next' in request.GET:
        next = request.GET.get('next')
    elif 'next' in request.POST:
        next = request.POST.get('next')
    if not next:
        next = getattr(settings, 'LOGIN_REDIRECT_URL', '/')
    return next

def passthrough_login_redirect_url(request, url):
    assert url.find("?") < 0 # TODO: Handle this case properly
    next = request.REQUEST.get('next')
    if next:
        url = url + '?' + urlencode(dict(next=next))
    return url


def generate_unique_username(txt):
    username = slugify(txt.split('@')[0])
    max_length = User._meta.get_field('username').max_length
    i = 0
    while True:
        try:
            if i:
                pfx = str(i+1)
            else:
                pfx = ''
            ret = username[0:max_length-len(pfx)] + pfx
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
