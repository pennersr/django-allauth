from django.conf import settings
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.core.validators import validate_email, ValidationError
from django.db.models import EmailField

from emailconfirmation.models import EmailAddress

def get_login_redirect_url(request):
    """
    Returns a url to redirect to after the login
    """
    if 'next' in request.session:
        next = request.session['next']
        del request.session['next']
        return next
    elif 'next' in request.GET:
        return request.GET.get('next')
    elif 'next' in request.POST:
        return request.POST.get('next')
    else:
        return getattr(settings, 'LOGIN_REDIRECT_URL', '/')

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
        

def get_email_address(email, exclude_user=None):
    """
    Returns an EmailAddress instance matching the given email. Both
    User.email and EmailAddress.email are considered candidates. This
    was done to deal gracefully with inconsistencies that are inherent
    due to the duplication of the email field in User and
    EmailAddress.  In case a User.email match is found the result is
    returned in a temporary EmailAddress instance.
    """
    try:
        emailaddresses = EmailAddress.objects
        if exclude_user:
            emailaddresses = emailaddresses.exclude(user=exclude_user)
        ret = emailaddresses.get(email__iexact=email)
    except EmailAddress.DoesNotExist:
        try:
            users = User.objects
            if exclude_user:
                users = users.exclude(user=exclude_user)
            usr = users.get(email__iexact=email)
            ret = EmailAddress(user=usr,
                               email=email,
                               verified=False,
                               primary=True)
        except User.DoesNotExist:
            ret = None
    return ret
