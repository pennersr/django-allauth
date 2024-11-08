# Introduction

Welcome to the django-allauth API specification. This API is intended to be
consumed by two different kind of clients:

- Web applications running in a **browser** context. For example, a
  single-page React application, to which the end user can navigate using a web
  browser.

- Applications, **apps** for short, executing in non-browser contexts. For example,
  a mobile Android or iOS application.

The security considerations for these two usage types are different. In a
browser context, cookies play a role.  Without taking special precautions, your
web application may be vulnerable to Cross-Site Request Forgery attacks.  For
mobile applications, this does not apply.

The API can be used for both use cases. Differences in handling of security is
automatically adjusted for, based on the request path used to make the API call.
For example, signing up can either be done using the
`/_allauth/browser/v1/auth/signup` or the `/_allauth/app/v1/auth/signup`
endpoint. For the **browser** usage, session cookies and CSRF protection
applies. For the **app** usage, cookies play no role, instead, a session token
is used.  The paths of all endpoints are documented in the form of
`/_allauth/{client}/v1/auth/signup`. Depending on the client type (`{client}`),
there may be slight differences in request/response handling.  This is
documented where applicable.

# Scope

The following functionality is all in scope and handled as part of this API:

- Regular accounts:
  - Login
  - Signup
  - Password forgotten
  - Manage email (add, remove, verify, select a different primary)
  - Change password.
  - Verification of email addresses.
- Two-Factor Authentication:
  - Authentication using an authenticator code
  - (De)activate TOTP
  - (Re)generate recovery codes
- Third-party providers:
  - Authenticate by performing a browser-level redirect (synchronous request).
  - Authenticate by means of a provider token.
  - Connect additional provider accounts.
  - Disconnect existing provider accounts.
  - Setting a password in case no password was set, yet.
  - Querying additional information before signing up.
- Session management:
  - Listing all sessions for a user.
  - Signing out of any of those sessions.


# Browser Usage

For web applications running in a browser, routing needs to be setup correctly
such that the sessions initiated at the backend are accessible in the frontend.

## Routing

When using the API in a browser context, regular Django sessions are used, along
with the usual session cookies. There are several options for setting up the
routing of your application.


###  Single Domain Routing

With single domain, path-based routing, both your frontend and backend are
served from the same domain, for example `https://app.org`. You will have to
make sure that some paths are served by the frontend, and others by the backend.

### Sub-domain Routing

With sub-domain based routing, the frontend and backend are served from
different domains.  However, as session cookies are used, these different
domains must share common main domain.

For example, you may use `app.project.org` for the frontend, which
interfaces with the backend over at `backend.project.org`.  In this
setup, Django will need to be configured with:

```
SESSION_COOKIE_DOMAIN = "project.org"
CSRF_COOKIE_DOMAIN = "project.org"
```

If your organization hosts unrelated applications, for example, a CMS for
marketing purposes, on the top level domain (`project.org`), it is not advisable
to set the session cookie domain to `project.org`, as those other applications
could get access to the session cookie. In that case, it is advised to use
`backend.app.project.org` for the backend, and set the session cookie domain to
`app.project.org`.

# App Usage

For app based usage, cookies play no role, yet, sessions are still used. When a
user walks through the authentication flow, a session is created.  Having an
authenticated session is proof that the user is allowed to further interact with
the backend. Unauthenticated sessions are also needed to remember state while
the user proceeds to go over the required steps necessary to authenticate.


## Session Tokens

Given that there is no cookie to point to the session, the header
`X-Session-Token` is used instead. The way of working is as follows:

- If you do not have a session token yet, do not send the `X-Session-Token` header.

- When making requests, session tokens can appear in the metadata
  (`meta.session_token`) of authentication related responses. If a session
  token appears, store it (overwriting any previous session token), and ensure
  to add the token to the `X-Session-Token` header of all subsequent requests.

- When receiving an authentication related response with status code 410
  (`Gone`), that is meant to indicate that the session is no longer valid.
  Remove the session token and start clean.


## Access Tokens

While session tokens are required to handle the authentication process,
depending on your requirements, a different type of token may be needed once
authenticated.

For example, your app likely needs access to other APIs as well. These APIs may
 even be implemented using different technologies, in which case having a
 stateless token, possibly a JWT encoding the user ID, might be a good fit.

In this API and its implementation no assumptions, and no (limiting) design
decisions are made in this regard. The token strategy of django-allauth is
pluggable, such that you can expose your own access token when the user
authenticates. As for as the API specification is concerned, the access token
will appear in the response of metadata (`meta.access_token`) of a successful
authentication request. How you can customize the token strategy can be found
over at the documentation of the `allauth.headless` Django application.


# Responses

Unless documented otherwise, responses are objects with the following
properties:
- The `status`, matching the HTTP status code.
- Data, if any, is returned as part of the `data` key.
- Metadata, if any, is returned as part of the `meta` key.
- Errors, if any, are listed in the `errors` key.

# Authentication Flows

In order to become authenticated, the user must complete a flow, potentially
consisting of several steps. For example:
- A login, after which the user is authenticated.
- A Login, followed by two-factor authentication, after which the user is
  authenticated.
- A signup, followed by mandatory email verification, after which the user is
  authenticated.

The API signals to the client that (re)authentication is required by means of a
`401` or `410` status code:
- Not authenticated: status `401`.
- Re-authentication required: status `401`, with `meta.is_authenticated = true`.
- Invalid session: status `410`. This only occurs for clients of type `app`.

All authentication related responses have status `401` or `410`, and,
`meta.is_authenticated` indicating whether authentication, or re-authentication
is required.

The flows the client can perform to initiate or complete the authentication are
communicates as part of authentication related responses. The authentication can
be initiated by means of these flows:
- Login using a local account (`login`).
- Signup for a local account (`signup`).
- Login or signup using the third-party provider redirect flow (`provider_redirect`).
- Login or signup by handing over a third-party provider retrieved elsewhere (`provider_token`).
- Login using a special code (`login_by_code`).
- Login using a passkey (`mfa_login_webauthn`).
- Signup using a passkey (`mfa_signup_webauthn`).

Depending on the state of the account, and the configuration of django-allauth, the flows above
can either lead to becoming directly authenticated, or, to followup flows:
- Provider signup (`provider_signup`).
- Email verification (`verify_email`).
- Two-factor authentication required (TOTP, recovery codes, or WebAuthn) (`mfa_authenticate`).

While authenticated, re-authentication may be required to safeguard the account when sensitive actions
are performed. The re-authentication flows are the following:
- Re-authenticate using password (`reauthenticate`).
- Re-authenticate using a 2FA authenticator (TOTP, recovery codes, or WebAuthn) (`mfa_reauthenticate`).

# Security Considerations

## Input Sanitization

The Django framework, by design, does *not* perform input sanitization. For
example, there is nothing preventing end users from signing up using `<script>`
or `Robert'); DROP TABLE students` as a first name. Django relies on its
template language for proper escaping of such values and mitigate any XSS
attacks.

As a result, any `allauth.headless` client **must** have proper XSS protection
in place as well. Be prepared that, for example, the WebAuthn endpoints could
return authenticator names as follows:

    {
      "name": "<script>alert(1)</script>",
      "credential": {
        "type": "public-key",
        ...
      }
    }
