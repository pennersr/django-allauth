from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.template import RequestContext

from allauth.utils import import_callable
from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.helpers import import_path

from locale import get_default_locale_callable


class FacebookAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        uid = self.account.uid
        return 'http://graph.facebook.com/%s/picture?type=large' % uid

    def __unicode__(self):
        dflt = super(FacebookAccount, self).__unicode__()
        return self.account.extra_data.get('name', dflt)


class FacebookProvider(OAuth2Provider):
    id = 'facebook'
    name = 'Facebook'
    package = 'allauth.socialaccount.providers.facebook'
    account_class = FacebookAccount

    def __init__(self):
        self._locale_callable_cache = None
        super(FacebookProvider, self).__init__()

    def get_method(self):
        return self.get_settings().get('METHOD', 'oauth2')

    def get_login_url(self, request, **kwargs):
        method = kwargs.get('method', self.get_method())
        if method == 'js_sdk':
            next = "'%s'" % (kwargs.get('next') or '')
            ret = "javascript:FB_login(%s)" % next
        else:
            assert method == 'oauth2'
            ret = super(FacebookProvider, self).get_login_url(request,
                                                              **kwargs)
        return ret

    def _get_locale_callable(self):
        settings = self.get_settings()
        f = settings.get('LOCALE_FUNC')
        if f:
            f = import_callable(f)
        else:
            f = get_default_locale_callable()
        return f

    def get_locale_for_request(self, request):
        if not self._locale_callable_cache:
            self._locale_callable_cache = self._get_locale_callable()
        return self._locale_callable_cache(request)

    def get_default_scope(self):
        scope = []
        if QUERY_EMAIL:
            scope.append('email')
        return scope

    def media_js(self, request):
        perms = ','.join(self.get_scope())
        locale = self.get_locale_for_request(request)
        try:
            app = self.get_app(request)
        except SocialApp.DoesNotExist:
            raise ImproperlyConfigured("No Facebook app configured: please"
                                       " add a SocialApp using the Django"
                                       " admin")
        ctx =  {'facebook_app': app,
                'facebook_channel_url':
                request.build_absolute_uri(reverse('facebook_channel')),
                'facebook_perms': perms,
                'facebook_jssdk_locale': locale}
        return render_to_string('facebook/fbconnect.html',
                                ctx,
                                RequestContext(request))

providers.registry.register(FacebookProvider)
