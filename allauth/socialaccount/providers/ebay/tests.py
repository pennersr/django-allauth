from allauth.socialaccount.providers.oauth2.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import EbayProvider


class EBayTests(OAuth2TestsMixin, TestCase):
    provider_id = EBayProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "access_token": "test_token",
                "expires_in": 3600,
                "token_type": "Bearer",
                "refresh_token": "test_refresh_token",
                "userid": "test_user"
            }
        """,
        )


# Storing expected response

# { /* UserResponse */
# "accountType" : "AccountTypeEnum : [INDIVIDUAL,BUSINESS]",
# "businessAccount" :
# { /* BusinessAccount */
# "address" :
# { /* Address */
# "addressLine1" : "string",
# "addressLine2" : "string",
# "city" : "string",
# "country" : "CountryCodeEnum : [AD,AE,AF...]",
# "county" : "string",
# "postalCode" : "string",
# "stateOrProvince" : "string"},
# "doingBusinessAs" : "string",
# "email" : "string",
# "name" : "string",
# "primaryContact" :
# { /* Contact */
# "firstName" : "string",
# "lastName" : "string"},
# "primaryPhone" :
# { /* Phone */
# "countryCode" : "string",
# "number" : "string",
# "phoneType" : "string"},
# "secondaryPhone" :
# { /* Phone */
# "countryCode" : "string",
# "number" : "string",
# "phoneType" : "string"},
# "website" : "string"},
# "individualAccount" :
# { /* IndividualAccount */
# "email" : "string",
# "firstName" : "string",
# "lastName" : "string",
# "primaryPhone" :
# { /* Phone */
# "countryCode" : "string",
# "number" : "string",
# "phoneType" : "string"},
# "registrationAddress" :
# { /* Address */
# "addressLine1" : "string",
# "addressLine2" : "string",
# "city" : "string",
# "country" : "CountryCodeEnum : [AD,AE,AF...]",
# "county" : "string",
# "postalCode" : "string",
# "stateOrProvince" : "string"},
# "secondaryPhone" :
# { /* Phone */
# "countryCode" : "string",
# "number" : "string",
# "phoneType" : "string"}
# },
# "registrationMarketplaceId" : "MarketplaceIdEnum : [EBAY_AT,EBAY_AU,EBAY_BE...]",
# "status" : "UserStatusEnum : [CONFIRMED,UNCONFIRMED,ACCOUNTONHOLD...]",
# "userId" : "string",
# "username" : "string"}
