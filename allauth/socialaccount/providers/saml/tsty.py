
locals = {'self': "<allauth.socialaccount.providers.saml.provider.SAMLProvider object at 0x3ec90ff951c0>", 
          'data': "<onelogin.saml2.auth.OneLogin_Saml2_Auth object at 0x3ec90ffda7b0>", 
          'provider_config': 
          {'idp': 
           {'name': 'Eviden IdP', 
            'slo_url': 'https://wac.myeviden.com/sso_cond2fa_2023/SingleLogoutService', 
            'sso_url': 'https://wac.myeviden.com/sso_cond2fa_2023/SingleSignOnService', 
            'x509cert': '-----BEGIN CERTIFICATE-----MIIDujCCAqKgAwIBAgIUJ9SLom7Hfd/gc3UWmgnqy5E1pNQwDQYJKoZIhvcNAQELBQAwaDELMAkGA1UEBhMCUEwxDDAKBgNVBAcMA0JZRDEPMA0GA1UECgwGRVZJREVOMRAwDgYDVQQLDAdEQVMtV0FDMSgwJgYDVQQDDB9FdmlkZW4gUm9vdCBDQSAyMDIzIGZvciBXQUMgU1NPMB4XDTIzMDQxMTExMjYzM1oXDTMzMDQwODExMjYzM1owWjELMAkGA1UEBhMCUEwxDzANBgNVBAoMBkVWSURFTjERMA8GA1UECwwIREFTMi1XQUMxJzAlBgNVBAMMHnNzby0yMDIzXzIwMzMud2FjLm15ZXZpZGVuLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAO4G952lQWXbVIzNL1Dxz96aA1DXiXIpzIXSTNlCDvv8+W8CCYRi+T5BpWpZqIPt/x9ksp+eQiYujuzGGau7nlOF+Y+NzlIZ1S1AaeoQzAZx5BuB6mf3xfyYBADA9nlnIzU1azUxR55d749121pzCVrLNtMUBpStuMUcW3dBmReyrE4dGTkwzpiVcEmoe38AvXH82ZZBsMUkGruz1Pdg9NLpX3TkTDMyeA4zUzxIh+2mBADfRcLfbXclxDQ/CD/DgYsxXoiIcMEzx5RLz7yfQyb4/c8tpRbjn/jiGSCWhyvmQhStxyE6d3Oo5epb69mWV1wKF0cNss9r93N//jUbEz0CAwEAAaNqMGgwCQYDVR0TBAIwADALBgNVHQ8EBAMCBLAwMQYDVR0lBCowKAYIKwYBBQUHAwEGCCsGAQUFBwMCBggrBgEFBQcDAwYIKwYBBQUHAwgwGwYDVR0RBBQwEoIQd2FjLm15ZXZpZGVuLmNvbTANBgkqhkiG9w0BAQsFAAOCAQEAgvhcRxiqjTqTkb0f1mqdZQYEnGeTQVWweKSR7ZLMqz9MpSi8pvfPERcHINvF60+6TtrAibnawFmUSigafe/5xxnILWRZq91obCahsBfKO7BWP9Wdhvx/NgfAZJiZk5MstWWF6Vsop7iuKRvmL/xem+q0PS/sy2Ff9eYl9Ejc6lNhUG420wA4xJpLOActC3FCzo468msN2bFSYJKuwg25bwOa5FgAVECNXng4ocwzYs3LVsEcV6DPTIYezchnaHYCgs4GSTVvN7cqkebeAgS8JP967t0BfSayeKWSSSembWojPivO1WKTGE3XdPjlqhcyReBbYBTGE6XiqN/zMlbvXw==-----END CERTIFICATE-----', 
            'entity_id': 'urn:prod-1.us.auth0.com'}, 
            'advanced': {'strict': False}, 
            'attribute_mapping': {'uid': 'http://schemas.auth0.com/clientID', 
                                  'email': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress', 
                                  'surname': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname', 
                                  'username': 'http://schemas.auth0.com/clientID', 
                                  'firstname': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname', 
                                  'email_verified': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'}}, 
                                  'raw_attributes': {'uid': ['A786614'], 'email': ['brian.ray@eviden.com'], 'firstname': ['Brian'], 'surname': ['Ray']}, 
                                  'attributes': {'uid': '', 'email': '', 'surname': '', 'username': '', 'firstname': '', 'email_verified': ''}, 
                                  'attribute_mapping': {'uid': 'http://schemas.auth0.com/clientID', 
                                                        'email': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress', 
                                                        'surname': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname', 
                                                        'username': 'http://schemas.auth0.com/clientID', 
                                                        'firstname': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname', 
                                                        'email_verified': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'}, 
                                                        'key': 'email_verified', 
                                                        'provider_keys': ['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'], 
                                                        'provider_key': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress', 
                                                        'attribute_list': [''], 'email_verified': ''}


raw_attributes = {'uid': ['A786614'], 'email': ['brian.ray@eviden.com'], 'firstname': ['Brian'], 'surname': ['Ray']}

attribute_mapping =  {'uid': 'http://schemas.auth0.com/clientID', 
                                  'email': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress', 
                                  'surname': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname', 
                                  'username': 'http://schemas.auth0.com/clientID', 
                                  'firstname': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname', 
                                  'email_verified': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'}
attributes = {'uid': '', 'email': '', 'surname': '', 'username': '', 'firstname': '', 'email_verified': ''}
for key, provider_keys in attribute_mapping.items():
        if isinstance(provider_keys, str):
            provider_keys = [provider_keys]
        for provider_key in provider_keys:
            attribute_list = raw_attributes.get(provider_key, None)
            if attribute_list == None:
                 attribute_list = raw_attributes.get(key, [""])
            if len(attribute_list) > 0:
                attributes[key] = attribute_list[0]
                break 

print(attributes)
