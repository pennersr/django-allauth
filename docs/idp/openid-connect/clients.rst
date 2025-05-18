Clients
=======

The Open ID Connect clients (also commonly referred to as consumers, or applications) can be managed via the Django admin. A typical client configuration has the following properties:

Name
    The name of the client. This is displayed in the authorization page.

ID
    The client ID. This field is automatically populated.

Secret
    The client secret. When adding clients using the Django admin, the secret is
    automatically generated and displayed only once via a message at creation
    time.

Scopes
    The scope(s) the client is allowed to request. Values are provide line by line, e.g.::

      openid
      profile
      email

Default scopes
    In case the client does not specify any scope, this are the default scope
    that will be used. Values are provide line by line.

Grant types
    A list of allowed grant types. Provide one value per line, e.g.::

      authorization_code
      client_credentials
      refresh_token

CORS origins
    A list of allowed origins for cross-origin requests, one per line.

Redirect URIs
    A list of allowed redirect (callback) URLs, one per line.

Response types
    A list of allowed response types. Provide one value per line, e.g.::

      code

Skip consent
    When enabled, the consent page is silently skipped and all requested scopes are granted.

Type
    Confidential clients are clients that are able to securely authenticate with
    the authorization server as they are able to keep their registered client
    secret safe. Public clients, such as applications running in a browser or
    mobile device, are unable to keep the client secrets safe.
