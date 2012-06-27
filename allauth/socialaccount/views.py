from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from forms import DisconnectForm, SignupForm

import helpers


def signup(request, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse(connections))
    sociallogin = request.session.get('socialaccount_sociallogin')
    if not sociallogin:
        return HttpResponseRedirect(reverse('account_login'))
    form_class = kwargs.pop("form_class", SignupForm)
    template_name = kwargs.pop("template_name", 'socialaccount/signup.html')
    if request.method == "POST":
        form = form_class(request.POST, sociallogin=sociallogin)
        if form.is_valid():
            form.save(request=request)
            return helpers.complete_social_signup(request, sociallogin)
    else:
        form = form_class(sociallogin=sociallogin)
    dictionary = dict(site=Site.objects.get_current(),
                      account=sociallogin.account,
                      form=form)
    return render_to_response(template_name, dictionary, 
                              RequestContext(request))


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
        form = DisconnectForm(request.POST, user=request.user)
        if form.is_valid():
            messages.add_message(request, messages.INFO, 
                                 _('The social account has been disconnected'))
            form.save()
            form = None
    if not form:
        form = DisconnectForm(user=request.user)
    d = dict(form=form)
    return render_to_response(
            'socialaccount/connections.html',
            d,
            context_instance=RequestContext(request))
