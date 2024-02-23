from allauth.headless.base.views import APIView


class ProviderLoginView(APIView):
    pass


provider_login = ProviderLoginView.as_view()
