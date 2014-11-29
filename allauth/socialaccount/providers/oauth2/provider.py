from django.core.urlresolvers import reverse
from django.utils.http import urlencode

from allauth.socialaccount.providers.base import Provider
import ast


class OAuth2Provider(Provider):
    def get_login_url(self, request, **kwargs):
        url = reverse(self.id + "_login")
        if kwargs:
            url = url + '?' + urlencode(kwargs)
        return url

    def get_auth_params(self, request, action):
        settings = self.get_settings()
        return settings.get('AUTH_PARAMS', {})

    def get_scope(self):
        settings = self.get_settings()
        scope = settings.get('SCOPE')
        if scope is None:
            scope = self.get_default_scope()
        return scope

    def get_dynamic_auth_params(self, request, action):
        auth_params = self.get_auth_params(request, action)
        dynamic_auth_params = request.GET.get('auth_params', None)
        if dynamic_auth_params:
            if isinstance(dynamic_auth_params, (str, unicode)):
                try:
                    dynamic_auth_params = ast.literal_eval(str(dynamic_auth_params))
                except SyntaxError as e:
                    m, d = e
                    m += ''' %s : auth_params must be a string representation of a dictionary ''' \
                         '''in your templates. e.g. auth_params="{'access_type='online'}" ''' % d[3]
                    raise SyntaxError(m)
            auth_params.update(dynamic_auth_params)
        return auth_params

    def get_dynamic_scope(self, request):
        scope = self.get_scope()
        dynamic_scope = request.GET.get('scope', None)
        if dynamic_scope:
            scope.extend(dynamic_scope.split(','))
        return scope

    def get_default_scope(self):
        return []
