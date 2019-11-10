from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import DoximityProvider


class DoximityTests(OAuth2TestsMixin, TestCase):
    provider_id = DoximityProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
            "id": 41993552342,
            "npi": 1952635229,
            "firstname": "John",
            "middlename": "Henry",
            "maiden_name": null,
            "lastname": "Smith",
            "full_name": "Ahmed S Belal, MD",
            "gender": "M",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94107",
            "phone": "(650) 200-3901",
            "fax": "888-416-8572",
            "email": "abelalmd@example.com",
            "address_1": "500 3rd St.",
            "address_2": "Suite 510",
            "lat": 42.3663926,
            "lon": -71.051395,
            "additional_locations": [{
                "address_1": "12 Main st",
                "address_2": null,
                "city": "Cambridge",
                "state": "MA",
                "phone": "555-555-5555",
                "fax": null,
                "zip": "02138"
            }],
            "credentials": "MD",
            "verified": true,
            "description": "Chief of Cardiology",
            "medical_school": "UCSF School of Medicine",
            "residencies": ["Stanford Medical Center", "Mt Sinai Hospital"],
            "specialty": "Cardiology",
            "specialty_details": {
                "abbr": "Cards",
                "code": "CA00",
                "credential_id": 4,
                "name": "Cardiology",
                "id": "CA00"
            },
            "hospitals": [{
                "name": "Mills-Peninsula Health Services",
                "aha_id": "6930315"
            }],
            "subspecialties": ["General Cardiology", "Cardiac Disease"],
            "profile_photo": "https://s3.amazonaws.com/doximity_prod_uploads\
/profile_photos/7969/normal/profile.png",
            "colleague_count": 142
        }
""",
        )
