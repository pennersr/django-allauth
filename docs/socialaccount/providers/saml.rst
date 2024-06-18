SAML
----

SAML 2.0 is supported out of the box. However, the required dependencies are not
installed by default. Therefore, you will need to specifcy the ``saml`` extra when
installing the package::

    $ pip install "django-allauth[saml]"

When you need to support SAML based authentication, often you need to support
multiple organizations, each having their own SAML based Identity Provider
(IdP). The way this translates to allauth is as follows:

- The allauth SAML endpoints all include an organization slug. For example,
  ``/accounts/saml/<organization_slug>/login/`` is used to initiate the SAML login
  flow.

- The organization slug is used to lookup the SAML IdP configuration, which is
  stored in a ``SocialApp``, or, its settings based
  ``SOCIALACCOUNT_PROVIDERS['saml']['APPS']`` counterpart.

- As per the SAML specification, each IdP is identified by an entity ID. Entity
  IDs typically use a URI based notation, and are therefore not suitable to be
  used as the organization slug.  So, you need to be aware that allauth has two
  ways of identifying the ``SocialApp`` -- via the SAML entity ID, and, via the
  organization slug.

- For each user signing in via the SAML provider, a ``SocialAccount`` record is
  created. Here, the combination of ``SocialAccount.provider`` and
  ``SocialAccount.uid`` is expected to be unique. The ``uid`` identitifer is the
  SAML account ID which is locally unique within the IdP. Therefore, if you are
  using multiple IdP's ``SocialAccount.provider`` cannot be set to
  ``"saml"``. Instead, the IdP entity ID would be a good candidate.

- The SAML account attributes can differ per IdP. Therefore, additional
  configuration is needed to be able to extract relevant account attributes,
  such as the ``uid`` and ``email``. This is done by setting up an attribute
  mapping.

How all of the above is configured in practice is shown below. Note that here we
are using the settings based configuration, but you can setup the ``SocialApp``
via the Django admin as well:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        "saml": {
            # Here, each app represents the SAML provider configuration of one
            # organization.
            "APPS": [
                {
                    # Used for display purposes, e.g. over by: {% get_providers %}
                    "name": "Acme Inc",

                    # Accounts signed up via this provider will have their
                    # `SocialAccount.provider` value set to this ID. The combination
                    # of this value and the `uid` must be unique. The IdP entity ID is a
                    # good choice for this.
                    "provider_id": "urn:example.com",

                    # The organization slug is configured by setting the
                    # `client_id` value. In this example, the SAML login URL is:
                    #
                    #     /accounts/saml/acme-inc/login/
                    "client_id": "acme-inc",

                    # The fields above are common `SocialApp` fields. For SAML,
                    # additional configuration is needed, which is placed in
                    # `SocialApp.settings`:
                    "settings": {
                        # Mapping account attributes to upstream (IdP specific) attributes.
                        # If left empty, an attempt will be done to map the attributes using
                        # built-in defaults.
                        "attribute_mapping": {
                            "uid": "http://schemas.auth0.com/clientID",
                            "email_verified": "http://schemas.auth0.com/email_verified",
                            "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
                        },
                        # The configuration of the IdP.
                        "idp": {
                            # The entity ID of the IdP is required.
                            "entity_id": "urn:example.com",

                            # Then, you can either specify the IdP's metadata URL:
                            "metadata_url": "https://example.com/saml2/metadata",

                            # Or, you can inline the IdP parameters here as follows:
                            "sso_url": "https://example.com/saml2/sso",
                            "slo_url": "https://example.com/saml2/slo",
                            "x509cert": """
    -----BEGIN CERTIFICATE-----
    MIIDHTCCAgWgAwIBAgIJLogff5x+S0BlMA0GCSqGSIb3DQEBCwUAMCwxKjAoBgNV
    BAMTIWRldi1uYXAybWY1ZTFwMXR3Z2Rv................................
    ................................G7qmyqcXRaf9HAuL/MvWz6zd96Ay6WHM
    pXk92/DyUV48JxK/Bl7Bj8qjl5w5R7Dwps6wj+69PIAg
    -----END CERTIFICATE-----
    """,
                        },
                        # The configuration of the SP.
                        "sp": {
                            # Optional entity ID of the SP. If not set, defaults to the `saml_metadata` urlpattern
                            "entity_id": "https://serviceprovider.com/sso/sp/metadata.xml",
                        },

                        # Advanced settings.
                        "advanced": {
                            "allow_repeat_attribute_name": True,
                            "allow_single_label_domains": False,
                            "authn_request_signed": False,
                            "digest_algorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
                            "logout_request_signed": False,
                            "logout_response_signed": False,
                            "metadata_signed": False,
                            "name_id_encrypted": False,
                            "name_id_format": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
                            "private_key": "MIID/zCCAuegAwIBAg...VGgdy+xoA==",
                            "reject_deprecated_algorithm": True,
                            # Due to security concerns, IdP initiated SSO is rejected by default.
                            "reject_idp_initiated_sso": True,
                            "signature_algorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
                            "want_assertion_encrypted": False,
                            "want_assertion_signed": False,
                            "want_attribute_statement": True,
                            "want_message_signed": False,
                            "want_name_id": False,
                            "want_name_id_encrypted": False,
                            "x509cert": "MIIEvQIBADANB...oddbXECo=",
                        },
                        "contact_person": {
                            "technical": {
                                "givenName": "Alice",
                                "emailAddress": "alice@example.com",
                            },
                            "administrative": {
                                "givenName": "Bob",
                                "emailAddress": "bob@example.com",
                            },
                        },
                    },
                },
            ]
        }
    }


In your templates, you can construct login URLs using the following template tag::

    {% load socialaccount %}
    {% provider_login_url "<provider_id>" %}


The SAML provider has the following endpoints:

- ``/accounts/saml/<organization_slug>/login/``: Initiate a login.

- ``/accounts/saml/<organization_slug>/acs/``: Assertion Consumer Service URL.

- ``/accounts/saml/<organization_slug>/sls/``: Single Logout Service URL.

- ``/accounts/saml/<organization_slug>/metadata/``: Metadata URL.
