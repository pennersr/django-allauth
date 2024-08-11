import base64
from unittest.mock import patch

from django.test.client import Client

import pytest


@pytest.fixture
def client():
    client = Client(HTTP_HOST="example.com")
    return client


@pytest.fixture
def saml_settings(settings):
    settings.SOCIALACCOUNT_PROVIDERS = {
        "saml": {
            "APPS": [
                {
                    "client_id": "org",
                    "provider_id": "urn:dev-123.us.auth0.com",
                    "settings": {
                        "attribute_mapping": {
                            "uid": "http://schemas.auth0.com/clientID",
                            "email_verified": "http://schemas.auth0.com/email_verified",
                            "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
                        },
                        "idp": {
                            "name": "Test IdP",
                            "entity_id": "urn:dev-123.us.auth0.com",
                            "sso_url": "https://dev-123.us.auth0.com/samlp/456",
                            "slo_url": "https://dev-123.us.auth0.com/samlp/456",
                            "x509cert": "",
                        },
                        "advanced": {
                            "strict": False,
                        },
                    },
                }
            ]
        }
    }


@pytest.fixture
def acs_saml_response_factory():
    def factory(in_response_to=None):
        xml = f"""<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="123"  InResponseTo="{in_response_to or ''}"  Version="2.0" IssueInstant="2023-07-08T08:24:14.141Z"  Destination="https://allauth.org/accounts/org/acs/">
  <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">urn:dev-123.us.auth0.com
  </saml:Issuer>
  <samlp:Status>
    <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
  </samlp:Status>
  <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" Version="2.0" ID="123" IssueInstant="2023-07-08T08:24:14.094Z">
    <saml:Issuer>urn:dev-123.us.auth0.com
    </saml:Issuer>
    <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
      <SignedInfo>
        <CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
        <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
        <Reference URI="#123">
          <Transforms>
            <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
            <Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
          </Transforms>
          <DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
          <DigestValue>123
          </DigestValue>
        </Reference>
      </SignedInfo>
      <SignatureValue>If7dFg...
      </SignatureValue>
      <KeyInfo>
        <X509Data>
          <X509Certificate>MIIDHTCC...
          </X509Certificate>
        </X509Data>
      </KeyInfo>
    </Signature>
    <saml:Subject>
      <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified">google-oauth2|108204123456789
      </saml:NameID>
      <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
        <saml:SubjectConfirmationData NotOnOrAfter="2023-07-08T09:24:14.094Z" Recipient="https://allauth.org/accounts/org/acs/" InResponseTo="ONELOGIN_f293b01d18bb0ac85a611b35e0c898af582bcfdd"/>
      </saml:SubjectConfirmation>
    </saml:Subject>
    <saml:Conditions NotBefore="2023-07-08T08:24:14.094Z" NotOnOrAfter="2023-07-08T09:24:14.094Z">
      <saml:AudienceRestriction>
        <saml:Audience>https://allauth.org/accounts/org/metadata/
        </saml:Audience>
      </saml:AudienceRestriction>
    </saml:Conditions>
    <saml:AuthnStatement AuthnInstant="2023-07-08T08:24:14.094Z" SessionIndex="_qPrYdL0O8w3vdb8eCEY5ZtHe76LA8-JU">
      <saml:AuthnContext>
        <saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified
        </saml:AuthnContextClassRef>
      </saml:AuthnContext>
    </saml:AuthnStatement>
    <saml:AttributeStatement xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <saml:Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:string">google-oauth2|108204123456789
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:string">john.doe@email.org
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:string">John
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:string">John
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:string">john.doe@email.org
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.auth0.com/identities/default/provider" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:string">google-oauth2
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.auth0.com/identities/default/connection" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:string">google-oauth2
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.auth0.com/identities/default/isSocial" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:boolean">true
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.auth0.com/clientID" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:string">dummysamluid
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.auth0.com/created_at" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:anyType">Wed Jun 28 2023 17:53:49 GMT+0000 (Coordinated Universal Time)
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.auth0.com/email_verified" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:boolean">true
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.auth0.com/locale" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:string">en
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.auth0.com/nickname" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:string">john.doe
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.auth0.com/picture" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:string">https://lh3.googleusercontent.com/a/AAcHTtfZ0fEyL3BKP1Hk2v1bNwpJd6ckIeo6jSExlkVjMXaIpsY=s96-c
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://schemas.auth0.com/updated_at" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xs:anyType">Sat Jul 08 2023 06:13:07 GMT+0000 (Coordinated Universal Time)
        </saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="Role" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
         <saml:AttributeValue xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">view-profile</saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="Role" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
         <saml:AttributeValue xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">manage-account-links</saml:AttributeValue>
      </saml:Attribute>
    </saml:AttributeStatement>
  </saml:Assertion>
</samlp:Response>
"""
        return base64.b64encode(xml.encode("utf8")).decode("utf8")

    return factory


@pytest.fixture
def sls_saml_request():
    xml = "<dummy></dummy>"
    return base64.b64encode(xml.encode("utf8")).decode("utf8")


@pytest.fixture
def mocked_signature_validation():
    with patch("onelogin.saml2.utils.OneLogin_Saml2_Utils.validate_sign") as mock:
        mock.return_value = True
        yield
