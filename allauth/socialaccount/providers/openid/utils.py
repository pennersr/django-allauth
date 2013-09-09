import base64

from openid.store.interface import OpenIDStore as OIDStore
from openid.association import Association as OIDAssociation
from openid.extensions.sreg import SRegResponse
from openid.extensions.ax import FetchResponse

from allauth.utils import valid_email_or_none

from .models import OpenIDStore, OpenIDNonce


class AXAttribute:
    CONTACT_EMAIL = 'http://axschema.org/contact/email'


class SRegField:
    EMAIL = 'email'


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
