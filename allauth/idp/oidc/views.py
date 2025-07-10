from http import HTTPStatus
from typing import List, Optional

from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.signing import BadSignature, Signer
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.middleware.csrf import CsrfViewMiddleware
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views import View
from django.views.decorators.clickjacking import xframe_options_deny
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView

from oauthlib.oauth2.rfc6749 import errors
from oauthlib.oauth2.rfc6749.errors import InvalidScopeError, OAuth2Error

from allauth.account import app_settings as account_settings
from allauth.account.internal.decorators import login_not_required
from allauth.account.internal.userkit import str_to_user_id
from allauth.core.internal import jwkkit
from allauth.core.internal.httpkit import add_query_params, del_query_params
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.forms import (
    AuthorizationForm,
    ConfirmCodeForm,
    DeviceAuthorizationForm,
)
from allauth.idp.oidc.internal.oauthlib import device_codes
from allauth.idp.oidc.internal.oauthlib.server import get_device_server, get_server
from allauth.idp.oidc.internal.oauthlib.utils import (
    convert_response,
    extract_params,
    respond_html_error,
    respond_json_error,
)
from allauth.idp.oidc.models import Client
from allauth.utils import build_absolute_uri


@method_decorator(login_not_required, name="dispatch")
class ConfigurationView(View):
    def get(self, request):
        data = {
            "authorization_endpoint": build_absolute_uri(
                request, reverse("idp:oidc:authorization")
            ),
            "device_authorization_endpoint": build_absolute_uri(
                request, reverse("idp:oidc:device_code")
            ),
            "revocation_endpoint": build_absolute_uri(
                request, reverse("idp:oidc:revoke")
            ),
            "token_endpoint": build_absolute_uri(request, reverse("idp:oidc:token")),
            "userinfo_endpoint": build_absolute_uri(
                request, reverse("idp:oidc:userinfo")
            ),
            "jwks_uri": build_absolute_uri(request, reverse("idp:oidc:jwks")),
            "issuer": get_adapter().get_issuer(),
            "response_types_supported": self._get_response_types_supported(),
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
        }
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response

    def _get_response_types_supported(self) -> List[str]:
        response_types = set()
        for client in Client.objects.only("response_types").iterator():
            response_types.update(client.get_response_types())
        return list(sorted(response_types))


configuration = ConfigurationView.as_view()


@method_decorator(xframe_options_deny, name="dispatch")
@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_not_required, name="dispatch")
class AuthorizationView(FormView):
    form_class = AuthorizationForm
    template_name = "idp/oidc/authorization_form." + account_settings.TEMPLATE_EXTENSION

    def get(self, request, *args, **kwargs):
        response = self._login_required(request)
        if response:
            return response
        orequest = extract_params(self.request)
        try:
            server = get_server()
            self._scopes, self._request_info = server.validate_authorization_request(
                *orequest
            )
            if "none" in self._request_info.get("prompt", ()):
                oresponse = server.create_authorization_response(
                    *orequest, scopes=self._scopes
                )
                return convert_response(*oresponse)

        # Errors that should be shown to the user on the provider website
        except errors.FatalClientError as e:
            return respond_html_error(request, e)
        except errors.OAuth2Error as e:
            return HttpResponseRedirect(e.in_uri(e.redirect_uri))
        if self._request_info["request"].client.skip_consent:
            return self._skip_consent()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        signed_request_info = request.POST.get("request")
        if not signed_request_info:
            return HttpResponseRedirect(
                reverse("idp:oidc:authorization") + "?" + request.POST.urlencode()
            )
        response = self._login_required(request)
        if response:
            return response

        # This view is CSRF exempt, but, if this is not a client initial POST
        # request, we do want a properly CSRF protected view.
        reason = CsrfViewMiddleware(get_response=lambda req: None).process_view(
            request, None, (), {}
        )
        if reason:
            return HttpResponseForbidden(f"CSRF Failed: {reason}")

        try:
            signer = Signer()
            self._scopes, self._request_info = signer.unsign_object(signed_request_info)
        except BadSignature:
            raise PermissionDenied
        if request.POST.get("action") != "grant":
            return self._respond_with_access_denied()
        return super().post(request, *args, **kwargs)

    def _login_required(self, request) -> Optional[HttpResponse]:
        prompts = []
        prompt = request.GET.get("prompt")
        if prompt:
            prompts = prompt.split()
        if "login" in prompts:
            return self._handle_login_prompt(request, prompts)
        if "none" in prompts:
            return None
        if request.user.is_authenticated:
            return None
        return login_required()(None)(request)  # type:ignore[misc,type-var]

    def _handle_login_prompt(
        self, request: HttpRequest, prompts: List[str]
    ) -> HttpResponse:
        prompts.remove("login")
        next_url = request.get_full_path()
        if prompts:
            next_url = add_query_params(next_url, {"prompt": " ".join(prompts)})
        else:
            next_url = del_query_params(next_url, "prompt")
        params = {}
        params[REDIRECT_FIELD_NAME] = next_url
        path = reverse(
            "account_reauthenticate"
            if request.user.is_authenticated
            else "account_login"
        )
        return HttpResponseRedirect(add_query_params(path, params))

    def _skip_consent(self):
        scopes = self._request_info["request"].scopes
        form_kwargs = self.get_form_kwargs()
        form_kwargs["data"] = {
            "scopes": scopes,
            "request": "not-relevant-for-skip-consent",
        }
        form = self.form_class(**form_kwargs)
        if not form.is_valid():
            # Shouldn't occur.
            raise PermissionDenied()
        return self.form_valid(form)

    def _respond_with_access_denied(self):
        redirect_uri = self._request_info.get("redirect_uri")
        state = self._request_info.get("state")
        params = {"error": "access_denied"}
        if state:
            params["state"] = state
        return HttpResponseRedirect(add_query_params(redirect_uri, params))

    def get_form_kwargs(self) -> dict:
        ret = super().get_form_kwargs()
        ret.update({"requested_scopes": self._scopes, "user": self.request.user})
        return ret

    def get_initial(self):
        signer = Signer()
        ret = {}
        request_info = self._request_info
        request_info.pop("request", None)
        prompt = request_info.get("prompt")
        if isinstance(prompt, set):
            request_info["prompt"] = list(prompt)
        ret["request"] = signer.sign_object((self._scopes, request_info))
        return ret

    def form_valid(self, form):
        orequest = extract_params(self.request)
        scopes = form.cleaned_data["scopes"]
        credentials = {"user": self.request.user}
        credentials.update(self._request_info)
        try:
            email = form.cleaned_data.get("email")
            if email:
                credentials["email"] = email
            oresponse = get_server().create_authorization_response(
                *orequest, scopes=scopes, credentials=credentials
            )
            return convert_response(*oresponse)

        except errors.FatalClientError as e:
            return respond_html_error(self.request, e)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret.update(
            {
                "client": Client.objects.get(id=self._request_info["client_id"]),
                "site": get_current_site(self.request),
            }
        )
        return ret


authorization = AuthorizationView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_not_required, name="dispatch")
class DeviceCodeView(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        orequest = extract_params(request)
        try:
            headers, data, status = (
                get_device_server().create_device_authorization_response(*orequest)
            )
            if status == HTTPStatus.OK:
                client_id = request.POST["client_id"]
                scope: Optional[List[str]] = None
                if "scope" in request.POST:
                    scope = request.POST["scope"].split()
                    client = Client.objects.get(id=client_id)
                    if not set(scope).issubset(set(client.get_scopes())):
                        raise InvalidScopeError()
                device_codes.create(client_id, scope, data)
        except OAuth2Error as e:
            return HttpResponse(
                e.json, content_type="application/json", status=e.status_code
            )
        return convert_response(headers, data, status)


device_code = DeviceCodeView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_required, name="dispatch")
class DeviceAuthorizationView(View):
    def dispatch(self, request, *args, **kwargs):
        if "code" in request.GET:
            form = ConfirmCodeForm(request.GET)
            if form.is_valid():
                return self._dispatch_authorization(
                    request,
                    form.cleaned_data["code"],
                    form.device_code,
                    form.client,
                )
        else:
            form = ConfirmCodeForm()
        context = {
            "form": form,
            "autorization_url": reverse("idp:oidc:device_authorization"),
        }
        return render(
            request,
            "idp/oidc/device_authorization_code_form."
            + account_settings.TEMPLATE_EXTENSION,
            context,
        )

    def _dispatch_authorization(
        self, request, user_code: str, device_code: str, client: Client
    ):
        context = {"user_code": user_code, "client": client}
        if request.method == "POST":
            form = DeviceAuthorizationForm(request.POST)
            if form.is_valid():
                confirm = form.cleaned_data["action"] == "confirm"
                device_codes.confirm_or_deny_device_code(
                    request.user, device_code, confirm=confirm
                )
                if confirm:
                    template_name = "idp/oidc/device_authorization_confirmed."
                else:
                    template_name = "idp/oidc/device_authorization_denied."
                return render(
                    request,
                    template_name + account_settings.TEMPLATE_EXTENSION,
                    context,
                )
        else:
            form = DeviceAuthorizationForm()
        context["autorization_url"] = (
            reverse("idp:oidc:device_authorization")
            + "?"
            + urlencode({"code": user_code})
        )

        return render(
            request,
            "idp/oidc/device_authorization_confirm_form."
            + account_settings.TEMPLATE_EXTENSION,
            context,
        )


device_authorization = DeviceAuthorizationView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_not_required, name="dispatch")
class TokenView(View):

    def post(self, request):
        if request.POST.get("grant_type") == Client.GrantType.DEVICE_CODE:
            return self._post_device_token(request)
        return self._create_token_response(request)

    def _create_token_response(self, request, data: Optional[dict] = None):
        orequest = extract_params(request)
        oresponse = get_server(
            pre_token=[lambda orequest: self._pre_token(orequest, data)]
        ).create_token_response(*orequest)
        return convert_response(*oresponse)

    def _pre_token(self, orequest, data: Optional[dict]):
        if orequest.grant_type == Client.GrantType.DEVICE_CODE:
            assert data is not None  # nosec
            if scope := data.get("scope"):
                orequest.scope = scope
            orequest.user = get_user_model().objects.get(
                pk=str_to_user_id(data["user"])
            )

    def _post_device_token(self, request):
        try:
            data = device_codes.poll_device_code(request)
        except OAuth2Error as e:
            return HttpResponse(
                e.json, content_type="application/json", status=e.status_code
            )
        else:
            return self._create_token_response(request, data)


token = TokenView.as_view()


@method_decorator(login_not_required, name="dispatch")
class UserInfoView(View):

    def get(self, request):
        orequest = extract_params(request)
        try:
            oresponse = get_server().create_userinfo_response(*orequest)
            return convert_response(*oresponse)
        except OAuth2Error as e:
            return respond_json_error(request, e)


user_info = UserInfoView.as_view()


@method_decorator(login_not_required, name="dispatch")
class JwksView(View):
    def get(self, request, *args, **kwargs):
        keys = []
        for pem in [app_settings.PRIVATE_KEY]:
            jwk, _ = jwkkit.load_jwk_from_pem(pem)
            keys.append(jwk)
        response = JsonResponse({"keys": keys})
        response["Access-Control-Allow-Origin"] = "*"
        return response


jwks = JwksView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_not_required, name="dispatch")
class RevokeView(View):
    def post(self, request, *args, **kwargs):
        orequest = extract_params(request)
        oresponse = get_server().create_revocation_response(*orequest)
        return convert_response(*oresponse)


revoke = RevokeView.as_view()
