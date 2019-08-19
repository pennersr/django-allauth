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

from django.utils.decorators import method_decorator
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from allauth.account.decorators import verified_email_required


class VerifiedEmailRequiredMixin(LoginRequiredMixin):
    """
    This class is a version of the
    allauth.account.decorators.verified_email_required()
    decorator, it is meant to be use in a class-based view.
    """

    @method_decorator(verified_email_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Just override the dispatch() method to run
        the control before doing anything in the class
        """
        return super(VerifiedEmailRequiredMixin, self)
                    .dispatch(request, *args, **kwargs)
