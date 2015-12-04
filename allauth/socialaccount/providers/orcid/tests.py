from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import OrcidProvider


class OrcidTests(OAuth2TestsMixin, TestCase):
    provider_id = OrcidProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
            "message-version": "1.1",
            "orcid-profile": {
                "orcid-bio": {
                    "personal-details": {
                        "given-names": {
                            "value": "myname"
                        },
                        "other-names": {
                            "other-name": [
                                {
                                    "value": "myself"
                                }
                            ],
                            "visibility": "PUBLIC"
                        },
                        "family-name": {
                            "value": "mylastname"
                        }
                    },
                    "delegation": null,
                    "applications": null,
                    "contact-details": {
                        "email": [],
                        "address": {
                            "country": {
                                "value": "AR",
                                "visibility": "PUBLIC"
                            }
                        }
                    },
                    "keywords": {
                        "keyword": [
                            {
                                "value": "basil"
                            },
                            {
                                "value": "pizza"
                            }
                        ],
                        "visibility": "PUBLIC"
                    },
                    "scope": null,
                    "biography": {
                        "value": "mybio",
                        "visibility": "PUBLIC"
                    }
                },
                "group-type": null,
                "orcid-activities": {
                    "affiliations": null,
                    "orcid-works": {
                        "scope": null,
                        "orcid-work": [
                            {
                                "put-code": "394644",
                                "work-title": {
                                    "subtitle": null,
                                    "title": {
                                        "value": "titlepaper"
                                    }
                                },
                                "visibility": "PUBLIC",
                                "work-type": "CONFERENCE_PAPER",
                                "url": null,
                                "work-contributors": {
                                    "contributor": [
                                        {
                                            "contributor-attributes": {},
                                            "credit-name": {
                                                "value": "myname",
                                                "visibility": "PUBLIC"
                                            }
                                        }
                                    ]
                                },
                                "work-source": {
                                    "path": "0000-0001-6796-198X",
                                    "host": "sandbox.orcid.org",
                                    "uri": "http://sandbox.orcid.org/...98X",
                                    "value": null
                                }
                            }
                        ]
                    }
                },
                "orcid": null,
                "client-type": null,
                "orcid-history": {
                    "last-modified-date": {
                        "value": 1406058219693
                    },
                    "creation-method": "WEBSITE",
                    "submission-date": {
                        "value": 1405935036511
                    },
                    "visibility": null,
                    "source": null,
                    "claimed": {
                        "value": true
                    }
                },
                "type": "USER",
                "orcid-preferences": {
                    "locale": "EN"
                },
                "orcid-identifier": {
                    "path": "0000-0001-6796-198X",
                    "host": "sandbox.orcid.org",
                    "uri": "http://sandbox.orcid.org/0000-0001-6796-198X",
                    "value": null
                }
            }
        }""")

    def get_login_response_json(self, with_refresh_token=True):
        # FIXME: This is not an actual response. I added this in order
        # to get the test suite going but did not verify to check the
        # exact response being returned.
        return """
        {
            "access_token": "testac",
            "expires_in": 631138026,
            "token_type": "bearer",
            "orcid": "0000-0001-6796-198X",
            "scope": "/orcid-profile/read-limited",
            "refresh_token": "testrf"
        }"""
