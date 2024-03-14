from django.http import HttpResponseRedirect
from django.urls import reverse

from allauth.socialaccount.models import SocialLogin


def get_pending_signup(request):
    data = request.session.get("socialaccount_sociallogin")
    if data:
        return SocialLogin.deserialize(data)


def redirect_to_signup(request, sociallogin):
    request.session["socialaccount_sociallogin"] = sociallogin.serialize()
    url = reverse("socialaccount_signup")
    return HttpResponseRedirect(url)


def clear_pending_signup(request):
    request.session.pop("socialaccount_sociallogin", None)


def signup_by_form(request, sociallogin, form):
    from allauth.socialaccount.helpers import complete_social_signup

    clear_pending_signup(request)
    user, resp = form.try_save(request)
    if not resp:
        resp = complete_social_signup(request, sociallogin)
    return resp
