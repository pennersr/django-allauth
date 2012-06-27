"""
Parts derived from socialregistration and authorized by: alen, pinda
Inspired by:
    http://github.com/leah/python-oauth/blob/master/oauth/example/client.py
    http://github.com/facebook/tornado/blob/master/tornado/auth.py
"""

import urllib
import urllib2

from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _

# parse_qsl was moved from the cgi namespace to urlparse in Python2.6.
# this allows backwards compatibility
try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl

import oauth2 as oauth


def get_token_prefix(url):
    """
    Returns a prefix for the token to store in the session so we can hold
    more than one single oauth provider's access key in the session.

    Example:

        The request token url ``http://twitter.com/oauth/request_token``
        returns ``twitter.com``

    """
    return urllib2.urlparse.urlparse(url).netloc


class OAuthError(Exception):
    pass


class OAuthClient(object):

    def __init__(self, request, consumer_key, consumer_secret, request_token_url,
        access_token_url, authorization_url, callback_url, parameters=None):

        self.request = request

        self.request_token_url = request_token_url
        self.access_token_url = access_token_url
        self.authorization_url = authorization_url

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

        self.consumer = oauth.Consumer(consumer_key, consumer_secret)
        self.client = oauth.Client(self.consumer)

        self.signature_method = oauth.SignatureMethod_HMAC_SHA1()

        self.parameters = parameters

        self.callback_url = callback_url

        self.errors = []
        self.request_token = None
        self.access_token = None

    def _get_request_token(self):
        """
        Obtain a temporary request token to authorize an access token and to
        sign the request to obtain the access token
        """
        if self.request_token is None:
            rt_url = self.request_token_url + '?' + urllib.urlencode({'oauth_callback': self.request.build_absolute_uri(self.callback_url)})
            response, content = self.client.request(rt_url, "GET")
            if response['status'] != '200':
                raise OAuthError(
                    _('Invalid response while obtaining request token from "%s".') % get_token_prefix(self.request_token_url))
            self.request_token = dict(parse_qsl(content))
            self.request.session['oauth_%s_request_token' % get_token_prefix(self.request_token_url)] = self.request_token
        return self.request_token

    def get_access_token(self):
        """
        Obtain the access token to access private resources at the API endpoint.
        """
        if self.access_token is None:
            request_token = self._get_rt_from_session()
            token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
            self.client = oauth.Client(self.consumer, token)
            at_url = self.access_token_url

            # Passing along oauth_verifier is required according to:
            # http://groups.google.com/group/twitter-development-talk/browse_frm/thread/472500cfe9e7cdb9#
            # Though, the custom oauth_callback seems to work without it?
            if self.request.REQUEST.has_key('oauth_verifier'):
                at_url = at_url + '?' + urllib.urlencode({'oauth_verifier': self.request.REQUEST['oauth_verifier']})
            response, content = self.client.request(at_url, "GET")
            if response['status'] != '200':
                raise OAuthError(
                    _('Invalid response while obtaining access token from "%s".') % get_token_prefix(self.request_token_url))
            self.access_token = dict(parse_qsl(content))

            self.request.session['oauth_%s_access_token' % get_token_prefix(self.request_token_url)] = self.access_token
        return self.access_token

    def _get_rt_from_session(self):
        """
        Returns the request token cached in the session by ``_get_request_token``
        """
        try:
            return self.request.session['oauth_%s_request_token' % get_token_prefix(self.request_token_url)]
        except KeyError:
            raise OAuthError(_('No request token saved for "%s".') % get_token_prefix(self.request_token_url))

    def _get_authorization_url(self):
        request_token = self._get_request_token()
        return '%s?oauth_token=%s&oauth_callback=%s' % (self.authorization_url,
            request_token['oauth_token'], self.request.build_absolute_uri(self.callback_url))

    def is_valid(self):
        try:
            self._get_rt_from_session()
            self.get_access_token()
        except OAuthError, e:
            self.errors.append(e.args[0])
            return False
        return True

    def get_redirect(self):
        """
        Returns a ``HttpResponseRedirect`` object to redirect the user to the
        URL the OAuth provider handles authorization.
        """
        return HttpResponseRedirect(self._get_authorization_url())


class OAuth(object):
    """
    Base class to perform oauth signed requests from access keys saved in a user's
    session.
    See the ``OAuthTwitter`` class below for an example.
    """

    def __init__(self, request, consumer_key, secret_key, request_token_url):
        self.request = request

        self.consumer_key = consumer_key
        self.secret_key = secret_key
        self.consumer = oauth.Consumer(consumer_key, secret_key)

        self.request_token_url = request_token_url

    def _get_at_from_session(self):
        """
        Get the saved access token for private resources from the session.
        """
        try:
            return self.request.session['oauth_%s_access_token' % get_token_prefix(self.request_token_url)]
        except KeyError:
            raise OAuthError(
                _('No access token saved for "%s".') % get_token_prefix(self.request_token_url))

    def query(self, url, method="GET", params=dict(), headers=dict()):
        """
        Request a API endpoint at ``url`` with ``params`` being either the
        POST or GET data.
        """
        access_token = self._get_at_from_session()

        token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])

        client = oauth.Client(self.consumer, token)

        body = urllib.urlencode(params)

        response, content = client.request(url, method=method, headers=headers,
            body=body)

        if response['status'] != '200':
            raise OAuthError(
                _('No access to private resources at "%s".') % get_token_prefix(self.request_token_url))

        return content
