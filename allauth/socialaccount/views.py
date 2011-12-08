from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.sites.models import Site

from allauth.utils import get_login_redirect_url
from allauth.account.views import signup as account_signup

from models import SocialAccount
from forms import DisconnectForm, SignupForm

import helpers

def signup(request, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse(connections))
    signup = request.session.get('socialaccount_signup')
    if not signup:
        return HttpResponseRedirect(reverse('account_login'))
    form_class = kwargs.pop("form_class", SignupForm)
    template_name = kwargs.pop("template_name", 
                               'socialaccount/signup.html')
    data = signup['data']
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            user = form.save(request=request)
            user.last_name = data.get('last_name', '')
            user.first_name = data.get('first_name', '')
            user.save()
            account = signup['account']
            account.user = user
            account.sync(data)
            return helpers.complete_social_signup(request, user, account)
    else:
        form = form_class(initial=data)
    dictionary = dict(site=Site.objects.get_current(),
                      account=signup['account'],
                      form=form)
    return render_to_response(template_name, 
                              dictionary, 
                              RequestContext(request))


def login_cancelled(request):
    d = { }
    return render_to_response('socialaccount/login_cancelled.html', 
                              d, context_instance=RequestContext(request))

def login_error(request):
    return helpers.render_authentication_error(request)


@login_required
def connections(request):
    form = None
    if request.method == 'POST':
        form = DisconnectForm(request.POST, user=request.user)
        if form.is_valid():
            messages.add_message \
            (request, messages.INFO, 
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
