OpenID
------

The OpenID provider requires dependencies that are not installed by
default. Install using::

    $ pip install "django-allauth[socialaccount,openid]"

The provider does not require any settings per se. However, a typical OpenID
login page presents the user with a predefined list of OpenID providers and
allows the user to input their own OpenID identity URL in case their provider is
not listed by default. The list of providers displayed by the builtin templates
can be configured as follows:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'openid': {
            'SERVERS': [
                {
                    'id': 'yahoo',
                    'name': 'Yahoo',
                    'openid_url': 'http://me.yahoo.com',
                },
                {
                    'id': 'hyves',
                    'name': 'Hyves',
                    'openid_url': 'http://hyves.nl',
                },
                {
                    'id': 'google',
                    'name': 'Google',
                    'openid_url': 'https://www.google.com/accounts/o8/id',
                },
            ]
        }
    }

You can manually specify extra_data you want to request from server as follows::

    SOCIALACCOUNT_PROVIDERS = \
        { 'openid':
            { 'SERVERS':
                [
                    {
                        'id': 'mojeid',
                        'name': 'MojeId',
                        'openid_url': 'https://mojeid.cz/endpoint/',
                        'extra_attributes': [
                            ('phone', ''http://axschema.org/contact/phone/default', False),
                            ('birth_date', 'http://axschema.org/birthDate', False),
                        ]
                    },
                ]
            }
        }

Attributes are in form (id, name, required) where id is key in extra_data field of socialaccount,
name is identifier of requested attribute and required specifies whether attribute is required.

If you want to manually include login links yourself, you can use the
following template tag:

.. code-block:: python

    {% load socialaccount %}
    <a href="{% provider_login_url "openid" openid="https://www.google.com/accounts/o8/id" next="/success/url/" %}">Google</a>

The OpenID provider can be forced to operate in stateless mode as follows::

    SOCIALACCOUNT_PROVIDERS = \
        { 'openid':
            { 'SERVERS':
                [
                    {
                        'id': 'steam',
                        'name': 'Steam',
                        'openid_url': 'https://steamcommunity.com/openid',
                        'stateless': True,
                    },
                ]
            }
        }
