from django.conf import settings
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

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
        
