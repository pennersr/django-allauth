Client ID Metadata Document
===========================

Support for the Client ID Metadata Document (`draft-ietf-oauth-client-id-metadata-document
<https://datatracker.ietf.org/doc/draft-ietf-oauth-client-id-metadata-document/>`_) can be
turned on via ``IDP_OIDC_CIMD_ENABLED``.

When enabled, clients can use an HTTPS URL as their ``client_id``. The
authorization server will fetch the metadata document from that URL to obtain the
client's registration information. No prior registration (such as Dynamic Client
Registration) is required. CIMD clients are always public clients and must use
PKCE.

By default, no hosts are allowed. Use ``IDP_OIDC_CIMD_ALLOWED_HOSTS`` to list
the hosts from which metadata documents may be fetched, for example::

    IDP_OIDC_CIMD_ALLOWED_HOSTS = [
        "chatgpt.com",
        "claude.ai",
    ]

Hostnames are matched exactly. To allow any host, use ``["*"]``. Doing so
allows unauthenticated clients to cause the authorization server to issue HTTPS
requests to arbitrary hosts, so a specific allowlist is recommended.

The fetched metadata is cached for the duration specified by
``IDP_OIDC_CIMD_CACHE_TIMEOUT`` (default: 3600 seconds). Rate limiting and a
per-``client_id`` lock prevent excessive outbound fetches.

For more advanced URL policies, override the ``is_cimd_url_allowed()`` adapter
method.
