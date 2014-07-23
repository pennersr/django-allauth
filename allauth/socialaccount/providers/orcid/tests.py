from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import OrcidProvider


class OrcidTests(create_oauth2_tests(registry.by_id(OrcidProvider.id))):
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
                                    "uri": "http://sandbox.orcid.org/0000-0001-6796-198X",
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
