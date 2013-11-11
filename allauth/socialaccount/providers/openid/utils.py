import base64

from openid.store.interface import OpenIDStore as OIDStore
from openid.association import Association as OIDAssociation
from openid.extensions.sreg import SRegResponse
from openid.extensions.ax import FetchResponse

from allauth.utils import valid_email_or_none

from .models import OpenIDStore, OpenIDNonce


class OldAXAttribute:
    PERSON_NAME = 'http://openid.net/schema/namePerson'
    PERSON_FIRST_NAME = 'http://openid.net/schema/namePerson/first'
    PERSON_LAST_NAME = 'http://openid.net/schema/namePerson/last'


class AXAttribute:
    CONTACT_EMAIL = 'http://axschema.org/contact/email'
    PERSON_NAME = 'http://axschema.org/namePerson'
    PERSON_FIRST_NAME = 'http://axschema.org/namePerson/first'
    PERSON_LAST_NAME = 'http://axschema.org/namePerson/last'


AXAttributes = [
    AXAttribute.CONTACT_EMAIL,
    AXAttribute.PERSON_NAME,
    AXAttribute.PERSON_FIRST_NAME,
    AXAttribute.PERSON_LAST_NAME,
    OldAXAttribute.PERSON_NAME,
    OldAXAttribute.PERSON_FIRST_NAME,
    OldAXAttribute.PERSON_LAST_NAME,
]


class SRegField:
    EMAIL = 'email'
    NAME = 'fullname'


SRegFields = [
    SRegField.EMAIL,
    SRegField.NAME,
]


class DBOpenIDStore(OIDStore):
    max_nonce_age = 6 * 60 * 60

    def storeAssociation(self, server_url, assoc=None):
        OpenIDStore.objects.create(
            server_url=server_url,
            handle=assoc.handle,
            secret=base64.encodestring(assoc.secret),
            issued=assoc.issued,
            lifetime=assoc.lifetime,
            assoc_type=assoc.assoc_type
        )

    def getAssociation(self, server_url, handle=None):
        stored_assocs = OpenIDStore.objects.filter(
            server_url=server_url
        )
        if handle:
            stored_assocs = stored_assocs.filter(handle=handle)

        stored_assocs.order_by('-issued')

        if stored_assocs.count() == 0:
            return None

        return_val = None

        for stored_assoc in stored_assocs:
            assoc = OIDAssociation(
                stored_assoc.handle, base64.decodestring(stored_assoc.secret.encode('utf-8')),
                stored_assoc.issued, stored_assoc.lifetime, stored_assoc.assoc_type
            )

            if assoc.getExpiresIn() == 0:
                stored_assoc.delete()
            else:
                if return_val is None:
                    return_val = assoc

        return return_val

    def removeAssociation(self, server_url, handle):
        stored_assocs = OpenIDStore.objects.filter(
            server_url=server_url
        )
        if handle:
            stored_assocs = stored_assocs.filter(handle=handle)

        stored_assocs.delete()

    def useNonce(self, server_url, timestamp, salt):
        try:
            OpenIDNonce.objects.get(
                server_url=server_url,
                timestamp=timestamp,
                salt=salt
            )
        except OpenIDNonce.DoesNotExist:
            OpenIDNonce.objects.create(
                server_url=server_url,
                timestamp=timestamp,
                salt=salt
            )
            return True

        return False


def get_email_from_response(response):
    email = None
    sreg = SRegResponse.fromSuccessResponse(response)
    if sreg:
        email = valid_email_or_none(sreg.get(SRegField.EMAIL))
    if not email:
        ax = FetchResponse.fromSuccessResponse(response)
        if ax:
            try:
                values = ax.get(AXAttribute.CONTACT_EMAIL)
                if values:
                    email = valid_email_or_none(values[0])
            except KeyError:
                pass
    return email


def get_value_from_response(response, sreg_names=None, ax_names=None):
    value = None
    if sreg_names:
        sreg = SRegResponse.fromSuccessResponse(response)
        if sreg:
            for name in sreg_names:
                value = sreg.get(name)
                if value:
                    break

    if not value and ax_names:
        ax = FetchResponse.fromSuccessResponse(response)
        if ax:
            for name in ax_names:
                try:
                    values = ax.get(name)
                    if values:
                        value = values[0]
                except KeyError:
                    pass
                if value:
                    break
    return value
