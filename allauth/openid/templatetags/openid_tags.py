from django.template.defaulttags import token_kwargs
from django import template
from django.core.urlresolvers import reverse
from django.utils.http import urlencode

register = template.Library()

class OpenIDLoginURLNode(template.Node):
    def __init__(self, params):
        self.params = params

    def render(self, context):
        url = reverse('openid_login')
        query = dict([(name, var.resolve(context)) for name, var
                      in self.params.iteritems()])
        if not query.has_key('next'):
            request = context['request']
            next = request.REQUEST.get('next')
            if next:
                query['next'] = next
        else:
            if not query['next']:
                del query['next']
        if query:
            url = url + '?' + urlencode(query)
        return url

def openid_login_url(parser, token):
    bits = token.split_contents()
    params = token_kwargs(bits[1:], parser, support_legacy=False)
    return OpenIDLoginURLNode(params)
    
def register_tags(reg):
    reg.tag()(openid_login_url)

register_tags(register)
