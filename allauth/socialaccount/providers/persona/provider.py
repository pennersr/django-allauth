import json

from django.template.loader import render_to_string
from django.template import RequestContext

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount, Provider


class PersonaAccount(ProviderAccount):
    def to_str(self):
        return self.account.uid

class PersonaProvider(Provider):
    id = 'persona'
    name = 'Persona'
    package = 'allauth.socialaccount.providers.persona'
    account_class = PersonaAccount

    def media_js(self, request):
        settings = self.get_settings()
        request_parameters = settings.get('REQUEST_PARAMETERS', {})
        ctx = { 'request_parameters': json.dumps(request_parameters) }
        return render_to_string('persona/auth.html',
                                ctx,
                                RequestContext(request))

    def get_login_url(self, request, **kwargs):
        return 'javascript:allauth.persona.login()'

providers.registry.register(PersonaProvider)
