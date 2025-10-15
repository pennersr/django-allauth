Introduction
============

The authentication process is an inherently stateful process, as unauthenticated
users are guided through a number of stages in order to become fully
authenticated.  For example, state is needed to keep track of a user that did
successfully complete the password stage, but did not yet pass the two-factor
authentication stage. Similarly, in case of email verificiation using a code, we
need to keep track of the code and keep track of the number of failed login
attempts.

The state of the authentication process is stored in the session. When using
allauth headless in non-browser contexts, such as mobile apps, there is no
session cookie that can be used to link clients to their session. So, instead of
relying on cookies, the HTTP header ``X-Session-Token`` is used to keep track
of the session.  The app is required to hand over the session token during the
authenticaton process.

Once a user is fully authenticated, you can hand out your own type of token by
setting up a specific :doc:`strategy`. Out of the box, two token strategies are
offered: :doc:`session-tokens` and :doc:`jwt-tokens`.
