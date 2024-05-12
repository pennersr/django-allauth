Email
=====

Case Sensitivity
****************

Historically, email addresses started out as case sensitive because the local
part (the part before the "@") could represent a case sensitive user
name. However, over time, this proved to be a bad idea and the RFCs that
succeeded the original were adjusted to move away from treating email addresses
as case sensitive.

- `RFC 821 <https://tools.ietf.org/html/rfc821>`_: The original RFC from 1982
  relies on case sensitivity.

- `RFC 2821 <https://tools.ietf.org/html/rfc2821>`_: Released in 2001, obsoletes
  RFC 821, yet, is still case sensitive.

- `RFC 5321 <https://datatracker.ietf.org/doc/html/rfc5321#section-4.1.2>`_: In
  2008, the "Local-part" is weakened to "MAY be case-sensitive".

- `RFC 6530 <https://tools.ietf.org/html/rfc6530#section-10.1>`_: In 2012, the
  following is acknowledged:

    It has long been the case that the email syntax permits choices about
    mailbox names that are **unwise in practice** [...].  The most often cited
    examples involve the use of **case-sensitivity** [...] in mailbox local
    parts.  These deliberately unusual constructions **are permitted** by the
    protocols, and servers are expected to support them.  Although they can
    provide value in special cases, taking advantage of them **is almost always
    bad practice** unless the intent is to create some form of **security by
    obscurity**.

To deal with this, previous versions of django-allauth used to store email
addresses in their original case, while performing lookups in a case insensitive
style. This approach led to subtle bugs in upstream code, and also comes at a
performance cost (``__iexact`` lookups). The latter requires case insensitive
index support, which not all databases support. Re-evaluating the approach in
current times has led to the conclusion that the benefits do not outweigh the
costs.  Therefore, email addresses are now always stored as lower case.
