# This file is from the requests-oauthlib library,
# https://github.com/requests/requests-oauthlib/blob/416d7382a193d180aac3a2fb7da6f621401ac960/requests_oauthlib/oauth1_auth.py
#
# The requests-oauthlib library is licensed under the ISC License:
#
# ISC License
#
# Copyright (c) 2014 Kenneth Reitz.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import logging
from requests.auth import AuthBase
from requests.utils import to_native_string

from oauthlib.common import extract_params
from oauthlib.oauth1 import (
    SIGNATURE_HMAC,
    SIGNATURE_TYPE_AUTH_HEADER,
    SIGNATURE_TYPE_BODY,
    Client,
)


CONTENT_TYPE_FORM_URLENCODED = "application/x-www-form-urlencoded"
CONTENT_TYPE_MULTI_PART = "multipart/form-data"


log = logging.getLogger(__name__)


# OBS!: Correct signing of requests are conditional on invoking OAuth1
# as the last step of preparing a request, or at least having the
# content-type set properly.
class OAuth1(AuthBase):
    """Signs the request using OAuth 1 (RFC5849)"""

    client_class = Client

    def __init__(
        self,
        client_key,
        client_secret=None,
        resource_owner_key=None,
        resource_owner_secret=None,
        callback_uri=None,
        signature_method=SIGNATURE_HMAC,
        signature_type=SIGNATURE_TYPE_AUTH_HEADER,
        rsa_key=None,
        verifier=None,
        decoding="utf-8",
        client_class=None,
        force_include_body=False,
        **kwargs,
    ):

        try:
            signature_type = signature_type.upper()
        except AttributeError:
            pass

        client_class = client_class or self.client_class

        self.force_include_body = force_include_body

        self.client = client_class(
            client_key,
            client_secret,
            resource_owner_key,
            resource_owner_secret,
            callback_uri,
            signature_method,
            signature_type,
            rsa_key,
            verifier,
            decoding=decoding,
            **kwargs,
        )

    def __call__(self, r):
        """Add OAuth parameters to the request.

        Parameters may be included from the body if the content-type is
        urlencoded, if no content type is set a guess is made.
        """
        # Overwriting url is safe here as request will not modify it past
        # this point.
        log.debug("Signing request %s using client %s", r, self.client)

        content_type = r.headers.get("Content-Type", "")
        if (
            not content_type
            and extract_params(r.body)
            or self.client.signature_type == SIGNATURE_TYPE_BODY
        ):
            content_type = CONTENT_TYPE_FORM_URLENCODED
        if not isinstance(content_type, str):
            content_type = content_type.decode("utf-8")

        is_form_encoded = CONTENT_TYPE_FORM_URLENCODED in content_type

        log.debug(
            "Including body in call to sign: %s",
            is_form_encoded or self.force_include_body,
        )

        if is_form_encoded:
            r.headers["Content-Type"] = CONTENT_TYPE_FORM_URLENCODED
            r.url, headers, r.body = self.client.sign(
                str(r.url), str(r.method), r.body or "", r.headers
            )
        elif self.force_include_body:
            # To allow custom clients to work on non form encoded bodies.
            r.url, headers, r.body = self.client.sign(
                str(r.url), str(r.method), r.body or "", r.headers
            )
        else:
            # Omit body data in the signing of non form-encoded requests
            r.url, headers, _ = self.client.sign(
                str(r.url), str(r.method), None, r.headers
            )

        r.prepare_headers(headers)
        r.url = to_native_string(r.url)
        log.debug("Updated url: %s", r.url)
        log.debug("Updated headers: %s", headers)
        log.debug("Updated body: %r", r.body)
        return r
