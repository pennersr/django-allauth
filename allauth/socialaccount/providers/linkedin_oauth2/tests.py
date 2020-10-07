# -*- coding: utf-8 -*-
from json import loads

from django.test.client import RequestFactory
from django.test.utils import override_settings

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.base import ProviderException
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import LinkedInOAuth2Provider


class LinkedInOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = LinkedInOAuth2Provider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
{
  "profilePicture": {
    "displayImage": "urn:li:digitalmediaAsset:12345abcdefgh-12abcd"
  },
  "id": "1234567",
  "lastName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Penners"
    }
  },
  "firstName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Raymond"
    }
  }
}
""",
        )

    def test_data_to_str(self):
        data = {
            "emailAddress": "john@doe.org",
            "firstName": "John",
            "id": "a1b2c3d4e",
            "lastName": "Doe",
            "pictureUrl": "https://media.licdn.com/mpr/foo",
            "pictureUrls": {
                "_total": 1,
                "values": ["https://media.licdn.com/foo"],
            },
            "publicProfileUrl": "https://www.linkedin.com/in/johndoe",
        }
        acc = SocialAccount(extra_data=data, provider="linkedin_oauth2")
        self.assertEqual(acc.get_provider_account().to_str(), "John Doe")

    def test_get_avatar_url_no_picture_setting(self):
        extra_data = """
{
  "profilePicture": {
    "displayImage": "urn:li:digitalmediaAsset:12345abcdefgh-12abcd"
  },
  "id": "1234567",
  "lastName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Penners"
    }
  },
  "firstName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Raymond"
    }
  }
}
"""
        acc = SocialAccount(
            extra_data=loads(extra_data),
            provider="linkedin_oauth2",
        )
        self.assertIsNone(acc.get_avatar_url())

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "linkedin_oauth2": {
                "PROFILE_FIELDS": [
                    "id",
                    "firstName",
                    "lastName",
                    "profilePicture(displayImage~:playableStreams)",
                ],
                "PROFILEPICTURE": {
                    "display_size_w_h": (400, 400.0),
                },
            },
        }
    )
    def test_get_avatar_url_with_setting(self):
        extra_data = """
{
  "profilePicture": {
    "displayImage": "urn:li:digitalmediaAsset:12345abcdefgh-12abcd"
  },
  "id": "1234567",
  "lastName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Penners"
    }
  },
  "firstName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Raymond"
    }
  }
}
"""
        acc = SocialAccount(
            extra_data=loads(extra_data),
            provider="linkedin_oauth2",
        )
        self.assertIsNone(acc.get_avatar_url())

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "linkedin_oauth2": {
                "PROFILE_FIELDS": [
                    "id",
                    "firstName",
                    "lastName",
                    "profilePicture(displayImage~:playableStreams)",
                ],
                "PROFILEPICTURE": {
                    "display_size_w_h": (100, 100.0),
                },
            },
        }
    )
    def test_get_avatar_url_with_picture(self):
        extra_data = """
{
  "profilePicture": {
    "displayImage": "urn:li:digitalmediaAsset:12345abcdefgh-12abcd"
  },
  "id": "1234567",
  "lastName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Penners"
    }
  },
  "firstName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Raymond"
    }
  },
  "profilePicture": {
    "displayImage~": {
      "elements": [
        {
          "authorizationMethod": "PUBLIC",
          "data": {
            "com.linkedin.digitalmedia.mediaartifact.StillImage": {
              "storageSize": {
                "height": 100,
                "width": 100
              },
              "storageAspectRatio": {
                "heightAspect": 1.0,
                "formatted": "1.00:1.00",
                "widthAspect": 1.0
              },
              "displaySize": {
                "height": 100.0,
                "width": 100.0,
                "uom": "PX"
              },
              "rawCodecSpec": {
                "name": "jpeg",
                "type": "image"
              },
              "displayAspectRatio": {
                "heightAspect": 1.0,
                "formatted": "1.00:1.00",
                "widthAspect": 1.0
              },
              "mediaType": "image/jpeg"
            }
          },
          "artifact": "urn:li:digitalmediaMediaArtifact:avatar",
          "identifiers": [
            {
              "identifierExpiresInSeconds": 4,
              "file": "urn:li:digitalmediaFile:this-is-the-link",
              "index": 0,
              "identifier": "this-is-the-link",
              "mediaType": "image/jpeg",
              "identifierType": "EXTERNAL_URL"
            }
          ]
        }
      ]
    }
  }
}
"""
        acc = SocialAccount(
            extra_data=loads(extra_data),
            provider="linkedin_oauth2",
        )
        self.assertEqual("this-is-the-link", acc.get_avatar_url())

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "linkedin_oauth2": {
                "PROFILE_FIELDS": [
                    "id",
                    "firstName",
                    "lastName",
                    "profilePicture(displayImage~:playableStreams)",
                ],
                "PROFILEPICTURE": {
                    "display_size_w_h": (400, 400.0),
                },
            },
        }
    )
    def test_get_avatar_url_size_mismatch(self):
        extra_data = """
{
  "profilePicture": {
    "displayImage": "urn:li:digitalmediaAsset:12345abcdefgh-12abcd"
  },
  "id": "1234567",
  "lastName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Penners"
    }
  },
  "firstName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Raymond"
    }
  },
  "profilePicture": {
    "displayImage~": {
      "elements": [
        {
          "authorizationMethod": "PUBLIC",
          "data": {
            "com.linkedin.digitalmedia.mediaartifact.StillImage": {
              "storageSize": {
                "height": 100,
                "width": 100
              },
              "storageAspectRatio": {
                "heightAspect": 1.0,
                "formatted": "1.00:1.00",
                "widthAspect": 1.0
              },
              "displaySize": {
                "height": 100.0,
                "width": 100.0,
                "uom": "PX"
              },
              "rawCodecSpec": {
                "name": "jpeg",
                "type": "image"
              },
              "displayAspectRatio": {
                "heightAspect": 1.0,
                "formatted": "1.00:1.00",
                "widthAspect": 1.0
              },
              "mediaType": "image/jpeg"
            }
          },
          "artifact": "urn:li:digitalmediaMediaArtifact:avatar",
          "identifiers": [
            {
              "identifierExpiresInSeconds": 4,
              "file": "urn:li:digitalmediaFile:this-is-the-link",
              "index": 0,
              "identifier": "this-is-the-link",
              "mediaType": "image/jpeg",
              "identifierType": "EXTERNAL_URL"
            }
          ]
        }
      ]
    }
  }
}
"""
        acc = SocialAccount(
            extra_data=loads(extra_data),
            provider="linkedin_oauth2",
        )
        self.assertIsNone(acc.get_avatar_url())

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "linkedin_oauth2": {
                "PROFILE_FIELDS": [
                    "id",
                    "firstName",
                    "lastName",
                    "profilePicture(displayImage~:playableStreams)",
                ],
                "PROFILEPICTURE": {
                    "display_size_w_h": (400, 400.0),
                },
            },
        }
    )
    def test_get_avatar_url_auth_mismatch(self):
        extra_data = """
{
  "profilePicture": {
    "displayImage": "urn:li:digitalmediaAsset:12345abcdefgh-12abcd"
  },
  "id": "1234567",
  "lastName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Penners"
    }
  },
  "firstName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Raymond"
    }
  },
  "profilePicture": {
    "displayImage~": {
      "elements": [
        {
          "authorizationMethod": "PRIVATE",
          "data": {
            "com.linkedin.digitalmedia.mediaartifact.StillImage": {
              "storageSize": {
                "height": 100,
                "width": 100
              },
              "storageAspectRatio": {
                "heightAspect": 1.0,
                "formatted": "1.00:1.00",
                "widthAspect": 1.0
              },
              "displaySize": {
                "height": 100.0,
                "width": 100.0,
                "uom": "PX"
              },
              "rawCodecSpec": {
                "name": "jpeg",
                "type": "image"
              },
              "displayAspectRatio": {
                "heightAspect": 1.0,
                "formatted": "1.00:1.00",
                "widthAspect": 1.0
              },
              "mediaType": "image/jpeg"
            }
          },
          "artifact": "urn:li:digitalmediaMediaArtifact:avatar",
          "identifiers": [
            {
              "identifierExpiresInSeconds": 4,
              "file": "urn:li:digitalmediaFile:this-is-the-link",
              "index": 0,
              "identifier": "this-is-the-link",
              "mediaType": "image/jpeg",
              "identifierType": "EXTERNAL_URL"
            }
          ]
        }
      ]
    }
  }
}
"""
        acc = SocialAccount(
            extra_data=loads(extra_data),
            provider="linkedin_oauth2",
        )
        self.assertIsNone(acc.get_avatar_url())

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "linkedin_oauth2": {
                "PROFILE_FIELDS": [
                    "id",
                    "firstName",
                    "lastName",
                    "profilePicture(displayImage~:playableStreams)",
                ],
                "PROFILEPICTURE": {
                    "display_size_w_h": (100, 100),
                },
            },
        }
    )
    def test_get_avatar_url_float_vs_int(self):
        extra_data = """
{
  "profilePicture": {
    "displayImage": "urn:li:digitalmediaAsset:12345abcdefgh-12abcd"
  },
  "id": "1234567",
  "lastName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Penners"
    }
  },
  "firstName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Raymond"
    }
  },
  "profilePicture": {
    "displayImage~": {
      "elements": [
        {
          "authorizationMethod": "PUBLIC",
          "data": {
            "com.linkedin.digitalmedia.mediaartifact.StillImage": {
              "storageSize": {
                "height": 100,
                "width": 100
              },
              "storageAspectRatio": {
                "heightAspect": 1.0,
                "formatted": "1.00:1.00",
                "widthAspect": 1.0
              },
              "displaySize": {
                "height": 100.0,
                "width": 100.0,
                "uom": "PX"
              },
              "rawCodecSpec": {
                "name": "jpeg",
                "type": "image"
              },
              "displayAspectRatio": {
                "heightAspect": 1.0,
                "formatted": "1.00:1.00",
                "widthAspect": 1.0
              },
              "mediaType": "image/jpeg"
            }
          },
          "artifact": "urn:li:digitalmediaMediaArtifact:avatar",
          "identifiers": [
            {
              "identifierExpiresInSeconds": 4,
              "file": "urn:li:digitalmediaFile:this-is-the-link",
              "index": 0,
              "identifier": "this-is-the-link",
              "mediaType": "image/jpeg",
              "identifierType": "EXTERNAL_URL"
            }
          ]
        }
      ]
    }
  }
}
"""
        acc = SocialAccount(
            extra_data=loads(extra_data),
            provider="linkedin_oauth2",
        )
        self.assertEqual("this-is-the-link", acc.get_avatar_url())

    def test_id_missing(self):
        extra_data = """
{
  "profilePicture": {
    "displayImage": "urn:li:digitalmediaAsset:12345abcdefgh-12abcd"
  },
  "Id": "1234567"
}
"""
        provider = LinkedInOAuth2Provider(RequestFactory().get("/login"))
        self.assertRaises(ProviderException, provider.extract_uid, loads(extra_data))
