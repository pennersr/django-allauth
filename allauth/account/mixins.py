"""
This module contain a class mixin design to bring email verification 
to class based views in django-allauth
It is used like django's LoginRequiedMixin, so when using this 
there is no need to use LoginRequiedMixin fro django

Example of use :

view.py

from django.views.generic import ListView
from allauth.account.mixins import VerifiedEmailRequiredMixin

class IndexView(VerifiedEmailRequiredMixin, ListView):
    ...
"""

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import EmailAddress
from .utils import send_email_confirmation


class VerifiedEmailRequiredMixin(LoginRequiredMixin):
    """
    This class is a version of the 
    allauth.account.decorators.verified_email_required() 
    decorator, it is meant to be use in a class-based view.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Just override the dispatch() method to run the control before doing anything in the class
        """
        if request.user.is_authenticated:
            if not EmailAddress.objects.filter(user=self.request.user,
                                               verified=True).exists():
                send_email_confirmation(request, request.user)
                return HttpResponseRedirect(reverse('account_email_verification_sent'))
        return super(VerifiedEmailRequiredMixin, self).dispatch(request, *args, **kwargs)
