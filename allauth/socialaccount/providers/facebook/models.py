from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.template import RequestContext

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import Provider, ProviderAccount

from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.models import SocialApp

class FacebookAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        uid = self.account.uid
        return 'http://graph.facebook.com/%s/picture?type=large' % uid

    def __unicode__(self):
        dflt = super(FacebookAccount, self).__unicode__()
        return self.account.extra_data.get('name', dflt)


class FacebookProvider(Provider):
    id = 'facebook'
    name = 'Facebook'
    package = 'allauth.socialaccount.providers.facebook'
    account_class = FacebookAccount

    def get_login_url(self, request, **kwargs):
        next = "'%s'" % (kwargs.get('next') or '')
        return "javascript:FB_login(%s)" % next
        

    def media_js(self, request):
        perm_list = []
        if QUERY_EMAIL:
            perm_list.append('email')
        perms = ','.join(perm_list)
        try:
            app = SocialApp.objects.get_current(self.id)
        except SocialApp.DoesNotExist:
            raise ImproperlyConfigured("No Facebook app configured: please"
                                       " add a SocialApp using the Django"
                                       " admin")
        ctx =  {'facebook_app': app,
                'facebook_channel_url': 
                request.build_absolute_uri(reverse('facebook_channel')),
                'facebook_perms': perms}
        return render_to_string('facebook/fbconnect.html', 
                                ctx,
                                RequestContext(request))

providers.registry.register(FacebookProvider)
