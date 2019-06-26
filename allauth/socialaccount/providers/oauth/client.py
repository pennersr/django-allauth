"""
Parts derived from socialregistration and authorized by: alen, pinda
Inspired by:
    http://github.com/leah/python-oauth/blob/master/oauth/example/client.py
    http://github.com/facebook/tornado/blob/master/tornado/auth.py
"""

import requests

from django.http import HttpResponseRedirect
from django.utils.http import urlencode
from django.utils.translation import gettext as _

from requests_oauthlib import OAuth1

from allauth.compat import parse_qsl, urlparse
from allauth.utils import build_absolute_uri, get_request_param


def get_token_prefix(url):
    """
    Returns a prefix for the token to store in the session so we can hold
    more than one single oauth provider's access key in the session.

    Example:

        The request token url ``http://twitter.com/oauth/request_token``
        returns ``twitter.com``

    """
    return urlparse(url).netloc


class OAuthError(Exception):
    pass


class OAuthClient(object):

    def __init__(self, request, consumer_key, consumer_secret,
                 request_token_url, access_token_url, callback_url,
                 parameters=None, provider=None):

        self.request = request

        self.request_token_url = request_token_url
        self.access_token_url = access_token_url

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

        self.parameters = parameters

        self.callback_url = callback_url
        self.provider = provider

        self.errors = []
        self.request_token = None
        self.access_token = None

    def _get_request_token(self):
        """
        Obtain a temporary request token to authorize an access token and to
        sign the request to obtain the access token
        """
        if self.request_token is None:
            get_params = {}
            if self.parameters:
                get_params.update(self.parameters)
            get_params['oauth_callback'] = build_absolute_uri(
                self.request, self.callback_url)
            rt_url = self.request_token_url + '?' + urlencode(get_params)
            oauth = OAuth1(self.consumer_key,
                           client_secret=self.consumer_secret)
            response = requests.post(url=rt_url, auth=oauth)
            if response.status_code not in [200, 201]:
                raise OAuthError(
                    _('Invalid response while obtaining request token'
                      ' from "%s".') % get_token_prefix(
                          self.request_token_url))
            self.request_token = dict(parse_qsl(response.text))
            self.request.session['oauth_%s_request_token' % get_token_prefix(
                self.request_token_url)] = self.request_token
        return self.request_token

    def get_access_token(self):
        """
        Obtain the access token to access private resources at the API
        endpoint.
        """
        if self.access_token is None:
            request_token = self._get_rt_from_session()
            oauth = OAuth1(
                self.consumer_key,
                client_secret=self.consumer_secret,
                resource_owner_key=request_token['oauth_token'],
                resource_owner_secret=request_token['oauth_token_secret'])
            at_url = self.access_token_url
            # Passing along oauth_verifier is required according to:
            # http://groups.google.com/group/twitter-development-talk/browse_frm/thread/472500cfe9e7cdb9#
            # Though, the custom oauth_callback seems to work without it?
            oauth_verifier = get_request_param(self.request, 'oauth_verifier')
            if oauth_verifier:
                at_url = at_url + '?' + urlencode(
                    {'oauth_verifier': oauth_verifier})
            response = requests.post(url=at_url, auth=oauth)
            if response.status_code not in [200, 201]:
                raise OAuthError(
                    _('Invalid response while obtaining access token'
                      ' from "%s".') % get_token_prefix(
                          self.request_token_url))
            self.access_token = dict(parse_qsl(response.text))

            self.request.session['oauth_%s_access_token' % get_token_prefix(
                self.request_token_url)] = self.access_token
        return self.access_token

    def _get_rt_from_session(self):
        """
        Returns the request token cached in the session by
        ``_get_request_token``
        """
        try:
            return self.request.session['oauth_%s_request_token'
                                        % get_token_prefix(
                                            self.request_token_url)]
        except KeyError:
            raise OAuthError(_('No request token saved for "%s".')
                             % get_token_prefix(self.request_token_url))

    def is_valid(self):
        try:
            self._get_rt_from_session()
            self.get_access_token()
        except OAuthError as e:
            self.errors.append(e.args[0])
            return False
        return True

    def get_redirect(self, authorization_url, extra_params):
        """
        Returns a ``HttpResponseRedirect`` object to redirect the user
        to the URL the OAuth provider handles authorization.
        """
        request_token = self._get_request_token()
        params = {'oauth_token': request_token['oauth_token'],
                  'oauth_callback': self.request.build_absolute_uri(
                      self.callback_url)}
        params.update(extra_params)
        url = authorization_url + '?' + urlencode(params)
        return HttpResponseRedirect(url)


class OAuth(object):
    """
    Base class to perform oauth signed requests from access keys saved
    in a user's session. See the ``OAuthTwitter`` class below for an
    example.
    """

    def __init__(self, request, consumer_key, secret_key, request_token_url):
        self.request = request
        self.consumer_key = consumer_key
        self.secret_key = secret_key
        self.request_token_url = request_token_url

    def _get_at_from_session(self):
        """
        Get the saved access token for private resources from the session.
        """
        try:
            return self.request.session['oauth_%s_access_token'
                                        % get_token_prefix(
                                            self.request_token_url)]
        except KeyError:
            raise OAuthError(
                _('No access token saved for "%s".')
                % get_token_prefix(self.request_token_url))

    def query(self, url, method="GET", params=dict(), headers=dict()):
        """
        Request a API endpoint at ``url`` with ``params`` being either the
        POST or GET data.
        """
        access_token = self._get_at_from_session()
        oauth = OAuth1(
            self.consumer_key,
            client_secret=self.secret_key,
            resource_owner_key=access_token['oauth_token'],
            resource_owner_secret=access_token['oauth_token_secret'])
        response = getattr(requests, method.lower())(url,
                                                     auth=oauth,
                                                     headers=headers,
                                                     params=params)
        if response.status_code != 200:
            raise OAuthError(
                _('No access to private resources at "%s".')
                % get_token_prefix(self.request_token_url))

        return response.text
