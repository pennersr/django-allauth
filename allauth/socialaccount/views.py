from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView

from ..account.views import CloseableSignupMixin, RedirectAuthenticatedUserMixin
from ..account.adapter import get_adapter as get_account_adapter

from .forms import DisconnectForm, SignupForm
from . import helpers


class SignupView(RedirectAuthenticatedUserMixin, CloseableSignupMixin, FormView):
    form_class = SignupForm
    template_name = 'socialaccount/signup.html'

    def dispatch(self, request, *args, **kwargs):
        self.sociallogin = request.session.get('socialaccount_sociallogin')
        if not self.sociallogin:
            return HttpResponseRedirect(reverse('account_login'))
        return super(SignupView, self).dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        ret = super(SignupView, self).get_form_kwargs()
        ret['sociallogin'] = self.sociallogin
        return ret
            
    def form_valid(self, form):
        form.save(self.request)
        return helpers.complete_social_signup(self.request, 
                                              self.sociallogin)

    def get_context_data(self, **kwargs):
        ret = super(SignupView, self).get_context_data(**kwargs)
        ret.update(dict(site=Site.objects.get_current(),
                        account=self.sociallogin.account))
        return ret

    def get_authenticated_redirect_url(self):
        return reverse(connections)

signup = SignupView.as_view()


def login_cancelled(request):
    d = {}
    return render_to_response('socialaccount/login_cancelled.html', d, 
                              context_instance=RequestContext(request))


def login_error(request):
    return helpers.render_authentication_error(request)


@login_required
def connections(request):
    form = None
    if request.method == 'POST':
        form = DisconnectForm(request.POST, request=request)
        if form.is_valid():
            get_account_adapter().add_message(request, 
                                              messages.INFO, 
                                              'socialaccount/messages/account_disconnected.txt')
            form.save()
            form = None
    if not form:
        form = DisconnectForm(request=request)
    d = dict(form=form)
    return render_to_response(
            'socialaccount/connections.html',
            d,
            context_instance=RequestContext(request))
