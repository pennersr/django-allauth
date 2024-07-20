from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import OrcidProvider


class OrcidTests(OAuth2TestsMixin, TestCase):
    provider_id = OrcidProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
    {
    "orcid-identifier": {
        "uri": "https://sandbox.orcid.org/0000-0001-6796-198X",
        "path": "0000-0001-6796-198X",
        "host": "sandbox.orcid.org"
    },
    "preferences": {
        "locale": "EN"
    },
    "history": {
        "creation-method": "MEMBER_REFERRED",
        "completion-date": null,
        "submission-date": {
        "value": 1456951327337
        },
        "last-modified-date": {
        "value": 1519493486728
        },
        "claimed": true,
        "source": null,
        "deactivation-date": null,
        "verified-email": true,
        "verified-primary-email": true
    },
    "person": {
        "last-modified-date": {
        "value": 1519493469738
        },
        "name": {
        "created-date": {
            "value": 1460669254582
        },
        "last-modified-date": {
            "value": 1460669254582
        },
        "given-names": {
            "value": "Patricia"
        },
        "family-name": {
            "value": "Lawrence"
        },
        "credit-name": null,
        "source": null,
        "visibility": "PUBLIC",
        "path": "0000-0001-6796-198X"
        },
        "other-names": {
        "last-modified-date": null,
        "other-name": [],
        "path": "/0000-0001-6796-198X/other-names"
        },
        "biography": {
        "created-date": {
            "value": 1460669254583
        },
        "last-modified-date": {
            "value": 1460669254583
        },
        "content": null,
        "visibility": "PUBLIC",
        "path": "/0000-0001-6796-198X/biography"
        },
        "researcher-urls": {
        "last-modified-date": null,
        "researcher-url": [],
        "path": "/0000-0001-6796-198X/researcher-urls"
        },
        "emails": {
        "last-modified-date": {
            "value": 1519493469738
        },
        "email": [
            {
            "created-date": {
                "value": 1456951327661
            },
            "last-modified-date": {
                "value": 1519493469738
            },
            "source": {
                "source-orcid": {
                "uri": "https://sandbox.orcid.org/0000-0001-6796-198X",
                "path": "0000-0001-6796-198X",
                "host": "sandbox.orcid.org"
                },
                "source-client-id": null,
                "source-name": {
                "value": "Patricia Lawrence"
                }
            },
            "email": "lawrencepatricia@mailinator.com",
            "path": null,
            "visibility": "PUBLIC",
            "verified": true,
            "primary": true,
            "put-code": null
            }
        ],
        "path": "/0000-0001-6796-198X/email"
        },
        "addresses": {
        "last-modified-date": null,
        "address": [],
        "path": "/0000-0001-6796-198X/address"
        },
        "keywords": {
        "last-modified-date": null,
        "keyword": [],
        "path": "/0000-0001-6796-198X/keywords"
        },
        "external-identifiers": {
        "last-modified-date": null,
        "external-identifier": [],
        "path": "/0000-0001-6796-198X/external-identifiers"
        },
        "path": "/0000-0001-6796-198X/person"
    },
    "activities-summary": {
        "last-modified-date": {
        "value": 1513777479628
        },
        "educations": {
        "last-modified-date": {
            "value": 1459957293365
        },
        "education-summary": [
            {
            "created-date": {
                "value": 1459957293365
            },
            "last-modified-date": {
                "value": 1459957293365
            },
            "source": {
                "source-orcid": {
                "uri": "https://sandbox.orcid.org/0000-0001-6796-198X",
                "path": "0000-0001-6796-198X",
                "host": "sandbox.orcid.org"
                },
                "source-client-id": null,
                "source-name": {
                "value": "Patricia Lawrence"
                }
            },
            "department-name": null,
            "role-title": null,
            "start-date": null,
            "end-date": null,
            "organization": {
                "name": "Polytech'Rambouillet",
                "address": {
                "city": "Rambouillet",
                "region": null,
                "country": "FR"
                },
                "disambiguated-organization": null
            },
            "visibility": "PUBLIC",
            "put-code": 19996,
            "path": "/0000-0001-6796-198X/education/19996"
            }
        ],
        "path": "/0000-0001-6796-198X/educations"
        },
        "employments": {
        "last-modified-date": {
            "value": 1513777479628
        },
        "employment-summary": [
            {
            "created-date": {
                "value": 1510399314937
            },
            "last-modified-date": {
                "value": 1513777479628
            },
            "source": {
                "source-orcid": {
                "uri": "https://sandbox.orcid.org/0000-0001-6796-198X",
                "path": "0000-0001-6796-198X",
                "host": "sandbox.orcid.org"
                },
                "source-client-id": null,
                "source-name": {
                "value": "Patricia Lawrence"
                }
            },
            "department-name": null,
            "role-title": null,
            "start-date": {
                "year": {
                "value": "2015"
                },
                "month": {
                "value": "03"
                },
                "day": {
                "value": "02"
                }
            },
            "end-date": null,
            "organization": {
                "name": "École nationale supérieure de céramique industrielle",
                "address": {
                "city": "Limoges",
                "region": null,
                "country": "FR"
                },
                "disambiguated-organization": {
                "disambiguated-organization-identifier": "105362",
                "disambiguation-source": "RINGGOLD"
                }
            },
            "visibility": "PUBLIC",
            "put-code": 29138,
            "path": "/0000-0001-6796-198X/employment/29138"
            },
            {
            "created-date": {
                "value": 1502366640610
            },
            "last-modified-date": {
                "value": 1513777467282
            },
            "source": {
                "source-orcid": {
                "uri": "https://sandbox.orcid.org/0000-0001-6796-198X",
                "path": "0000-0001-6796-198X",
                "host": "sandbox.orcid.org"
                },
                "source-client-id": null,
                "source-name": {
                "value": "Patricia Lawrence"
                }
            },
            "department-name": null,
            "role-title": null,
            "start-date": {
                "year": {
                "value": "2002"
                },
                "month": {
                "value": "02"
                },
                "day": {
                "value": "16"
                }
            },
            "end-date": {
                "year": {
                "value": "2015"
                },
                "month": {
                "value": "08"
                },
                "day": {
                "value": "12"
                }
            },
            "organization": {
                "name": "University of Cambridge",
                "address": {
                "city": "Cambridge",
                "region": "Cambridgeshire",
                "country": "GB"
                },
                "disambiguated-organization": {
                "disambiguated-organization-identifier": "2152",
                "disambiguation-source": "RINGGOLD"
                }
            },
            "visibility": "PUBLIC",
            "put-code": 27562,
            "path": "/0000-0001-6796-198X/employment/27562"
            }
        ],
        "path": "/0000-0001-6796-198X/employments"
        },
        "fundings": {
        "last-modified-date": null,
        "group": [],
        "path": "/0000-0001-6796-198X/fundings"
        },
        "peer-reviews": {
        "last-modified-date": null,
        "group": [],
        "path": "/0000-0001-6796-198X/peer-reviews"
        },
        "works": {
        "last-modified-date": {
            "value": 1459957753077
        },
        "group": [
            {
            "last-modified-date": {
                "value": 1459957753077
            },
            "external-ids": {
                "external-id": []
            },
            "work-summary": [
                {
                "put-code": 583440,
                "created-date": {
                    "value": 1459957753047
                },
                "last-modified-date": {
                    "value": 1459957753077
                },
                "source": {
                    "source-orcid": {
                    "uri": "https://sandbox.orcid.org/0000-0001-6796-198X",
                    "path": "0000-0001-6796-198X",
                    "host": "sandbox.orcid.org"
                    },
                    "source-client-id": null,
                    "source-name": {
                    "value": "Patricia Lawrence"
                    }
                },
                "title": {
                    "title": {
                    "value": "Standard & Poor's fiscal methodology reviewed"
                    },
                    "subtitle": null,
                    "translated-title": null
                },
                "external-ids": {
                    "external-id": []
                },
                "type": "JOURNAL_ARTICLE",
                "publication-date": {
                    "year": {
                    "value": "2001"
                    },
                    "month": {
                    "value": "07"
                    },
                    "day": {
                    "value": "14"
                    },
                    "media-type": null
                },
                "visibility": "PUBLIC",
                "path": "/0000-0001-6796-198X/work/583440",
                "display-index": "0"
                }
            ]
            }
        ],
        "path": "/0000-0001-6796-198X/works"
        },
        "path": "/0000-0001-6796-198X/activities"
    },
    "path": "/0000-0001-6796-198X"
    }
        """,
        )

    def get_expected_to_str(self):
        return "Orcid.org"

    def get_login_response_json(self, with_refresh_token=True):
        # TODO: This is not an actual response. I added this in order
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
