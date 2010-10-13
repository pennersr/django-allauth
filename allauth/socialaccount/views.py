from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib import messages
from django.contrib.sites.models import Site
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from models import SocialAccount
from forms import DisconnectForm

def signup(request):
    pass

def login(request):
    d = { 'site': Site.objects.get_current() }
    return render_to_response('socialaccount/login.html', d, context_instance=RequestContext(request))


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
