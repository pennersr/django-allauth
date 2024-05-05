from django.urls import include, path

from allauth.headless.socialaccount import views


def build_urlpatterns(client):
    return [
        path(
            "account/",
            include(
                [
                    path(
                        "providers",
                        views.ManageProvidersView.as_api_view(client=client),
                        name="manage_providers",
                    ),
                ]
            ),
        ),
        path(
            "auth/",
            include(
                [
                    path(
                        "provider/",
                        include(
                            [
                                path(
                                    "signup",
                                    views.ProviderSignupView.as_api_view(client=client),
                                    name="provider_signup",
                                ),
                                path(
                                    "redirect",
                                    views.RedirectToProviderView.as_api_view(
                                        client=client
                                    ),
                                    name="redirect_to_provider",
                                ),
                                path(
                                    "token",
                                    views.ProviderTokenView.as_api_view(client=client),
                                    name="provider_token",
                                ),
                            ]
                        ),
                    )
                ]
            ),
        ),
    ]
