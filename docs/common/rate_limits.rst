.. _rate_limits:

Rate Limits
===========

In order to be secure out of the box various rate limits are in place. The rate
limit mechanism is backed by a Django cache. Hence, rate limiting will not work
properly if you are using the `DummyCache`.

When rate limits are hit the ``429.html`` template is rendered,
alternatively, you can configure a custom handler by declaring
a ``handler429`` view in your root URLconf.

Rate limits are consumed by triggering actions, the full list of which is
documented below.  Per action, the rate can be configured. The rate itself is an
amount, per time unit, per either IP address, user or action-specific key.

For example, requesting a password reset is an action that is both limited
globally by IP address, as well as per email. Here, the email address used is
the specific key.


Implementation Notes
--------------------

The builtin rate limitting relies on a cache and uses non-atomic operations,
making it vulnerable to race conditions. As a result, users may occasionally
bypass the intended rate limit due to concurrent access. However, such race
conditions are rare in practice. For example, if the limit is set to 10 requests
per minute and a large number of parallel processes attempt to test that limit,
you may occasionally observe slight overruns—such as 11 or 12 requests slipping
through. Nevertheless, exceeding the limit by a large margin is highly unlikely
due to the low probability of many processes entering the critical non-atomic
code section simultaneously.


Testing
-------

Unless the rate limit is disabled or the default limits are increased, you might
run intro problems if you're running unit tests that are dependant on
funcionalities covered by the rate limits. For example, if you're testing the
`confirm_email` functionality in your unit tests and you're testing if the
verification email is sent twice after requesting it twice, only one of the
emails will be sent.
