from __future__ import annotations

import json
from http import HTTPStatus
from typing import Any

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.signing import BadSignature, Signer
from django.db import transaction
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

from oauthlib.common import Request
from oauthlib.oauth2.rfc6749 import errors
from oauthlib.oauth2.rfc6749.errors import InvalidScopeError, OAuth2Error

from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal.decorators import login_not_required
from allauth.core.exceptions import ImmediateHttpResponse, RateLimited
from allauth.core.internal import jwkkit, ratelimit
from allauth.core.internal.httpkit import (
    add_query_params,
    authenticated_user,
    del_query_params,
)
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.forms import (
    AuthorizationForm,
    ClientRegistrationForm,
    ConfirmCodeForm,
    DeviceAuthorizationForm,
    RPInitiatedLogoutForm,
)
from allauth.idp.oidc.internal import flows
from allauth.idp.oidc.internal.oauthlib import device_codes
from allauth.idp.oidc.internal.oauthlib.server import get_device_server, get_server
from allauth.idp.oidc.internal.oauthlib.utils import (
    convert_response,
    extract_params,
    get_validator_context,
    respond_html_error,
    respond_json_error,
)
from allauth.idp.oidc.internal.resources import get_resources
from allauth.idp.oidc.models import Client, Token
from allauth.utils import build_absolute_uri


class _ClientHttpResponseRedirect(HttpResponse):
    """
    Not using HttpResponseRedirect -- that one checks schemes, and here
    we might be redirecting to an app native url.
    """

    def __init__(self, redirect_uri: str):
        super().__init__(status=HTTPStatus.FOUND)
        self["Location"] = redirect_uri


def _enforce_csrf(request: HttpRequest) -> HttpResponseForbidden | None:
    """
    Scenario: view is CSRF exempt, but, if this is not a client initial POST
    request, we do want a properly CSRF protected view.
    """
    reason = CsrfViewMiddleware(
        get_response=lambda req: HttpResponseForbidden()
    ).process_view(request, lambda *args, **kwargs: HttpResponse(), (), {})
    if reason:
        return HttpResponseForbidden(f"CSRF Failed: {reason}")
    return None


@method_decorator(login_not_required, name="dispatch")
class ConfigurationView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        userinfo_endpoint = app_settings.USERINFO_ENDPOINT
        if not userinfo_endpoint:
            userinfo_endpoint = build_absolute_uri(
                request, reverse("idp:oidc:userinfo")
            )
        supported_types = self._get_supported_types()
        data = {
            "authorization_endpoint": build_absolute_uri(
                request, reverse("idp:oidc:authorization")
            ),
            "code_challenge_methods_supported": ["S256"],
            "device_authorization_endpoint": build_absolute_uri(
                request, reverse("idp:oidc:device_code")
            ),
            "end_session_endpoint": build_absolute_uri(
                request, reverse("idp:oidc:logout")
            ),
            "id_token_signing_alg_values_supported": ["RS256"],
            "issuer": get_adapter().get_issuer(),
            "jwks_uri": build_absolute_uri(request, reverse("idp:oidc:jwks")),
            "revocation_endpoint": build_absolute_uri(
                request, reverse("idp:oidc:revoke")
            ),
            "token_endpoint": build_absolute_uri(request, reverse("idp:oidc:token")),
            "token_endpoint_auth_methods_supported": app_settings.AUTH_METHODS,
            "userinfo_endpoint": userinfo_endpoint,
            "subject_types_supported": ["public"],
            **supported_types,
        }
        if app_settings.INTROSPECTION_ENABLED:
            data["introspection_endpoint"] = build_absolute_uri(
                request, reverse("idp:oidc:introspect")
            )
            data["introspection_endpoint_auth_methods_supported"] = (
                app_settings.INTROSPECTION_AUTH_METHODS
            )
        if app_settings.DCR_ENABLED:
            data["registration_endpoint"] = build_absolute_uri(
                request, reverse("idp:oidc:client_registration")
            )

        get_adapter().populate_server_metadata(data)
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response

    def _get_supported_types(self) -> dict[str, list[str]]:
        scopes_supported = ["openid", "profile", "email"]
        return {
            "scopes_supported": scopes_supported,
            "grant_types_supported": sorted(gt.value for gt in Client.GrantType),
            "response_types_supported": sorted(rt.value for rt in Client.ResponseType),
        }


configuration = ConfigurationView.as_view()


@method_decorator(xframe_options_deny, name="dispatch")
@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_not_required, name="dispatch")
class AuthorizationView(FormView):
    form_class = AuthorizationForm
    template_name = f"idp/oidc/authorization_form.{account_settings.TEMPLATE_EXTENSION}"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = self._login_required(request)
        if response:
            return response
        orequest = extract_params(self.request)
        try:
            server = get_server()
            self._scopes, self._request_info = server.validate_authorization_request(
                *orequest
            )
            self._request_info["resources"] = get_resources(request)
            if "none" in self._request_info.get("prompt", ()):
                oresponse = server.create_authorization_response(
                    *orequest, scopes=self._scopes
                )
                return convert_response(*oresponse)

        # Errors that should be shown to the user on the provider website
        except (errors.FatalClientError, ValidationError) as e:
            return respond_html_error(request, error=e)
        except errors.OAuth2Error as e:
            return _ClientHttpResponseRedirect(e.in_uri(e.redirect_uri))
        if self._request_info["request"].client.skip_consent:
            return self._skip_consent()
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        signed_request_info = request.POST.get("request")
        if not signed_request_info:
            return HttpResponseRedirect(
                f"{reverse('idp:oidc:authorization')}?{request.POST.urlencode()}"
            )
        response = self._login_required(request)
        if response:
            return response

        csrf_resp = _enforce_csrf(request)
        if csrf_resp:
            return csrf_resp

        try:
            signer = Signer()
            self._scopes, self._request_info = signer.unsign_object(signed_request_info)
        except BadSignature:
            raise PermissionDenied
        if request.POST.get("action") != "grant":
            return self._respond_with_access_denied()
        return super().post(request, *args, **kwargs)

    def _login_required(self, request: HttpRequest) -> HttpResponse | None:
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
        return login_required()(None)(request)  # type: ignore[misc,type-var]

    def _handle_login_prompt(
        self, request: HttpRequest, prompts: list[str]
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

    def _skip_consent(self) -> HttpResponse:
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

    def _respond_with_access_denied(self) -> HttpResponse:
        redirect_uri = self._request_info.get("redirect_uri")
        state = self._request_info.get("state")
        params = {"error": "access_denied"}
        if state:
            params["state"] = state
        return _ClientHttpResponseRedirect(add_query_params(redirect_uri, params))

    def get_form_kwargs(self) -> dict[str, Any]:
        ret = super().get_form_kwargs()
        ret.update({"requested_scopes": self._scopes, "user": self.request.user})
        return ret

    def get_initial(self) -> dict[str, Any]:
        signer = Signer()
        ret = {}
        request_info = self._request_info
        request_info.pop("request", None)
        prompt = request_info.get("prompt")
        if isinstance(prompt, set):
            request_info["prompt"] = list(prompt)
        ret["request"] = signer.sign_object((self._scopes, request_info))
        return ret

    def form_valid(self, form: AuthorizationForm) -> HttpResponse:
        orequest = extract_params(self.request)

        scopes = form.cleaned_data["scopes"]

        # oauthlib puts all credentials into its `Request`.
        credentials = {"user": self.request.user}
        credentials.update(self._request_info)
        credentials.pop("resources", None)

        ctx = get_validator_context()
        ctx.requested_resources = self._request_info.get("resources")

        try:
            email = form.cleaned_data.get("email")
            if email:
                ctx.email = email
            oresponse = get_server().create_authorization_response(
                *orequest, scopes=scopes, credentials=credentials
            )
            return convert_response(*oresponse)

        except errors.FatalClientError as e:
            return respond_html_error(self.request, error=e)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
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
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        orequest = extract_params(request)
        try:
            get_validator_context().requested_resources = get_resources(request)
            headers, data, status = (
                get_device_server().create_device_authorization_response(*orequest)
            )
            if status == HTTPStatus.OK:
                client_id = request.POST["client_id"]
                scope: list[str] | None = None
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
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
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
            f"idp/oidc/device_authorization_code_form.{account_settings.TEMPLATE_EXTENSION}",
            context,
        )

    def _dispatch_authorization(
        self, request: HttpRequest, user_code: str, device_code: str, client: Client
    ) -> HttpResponse:
        context = {"user_code": user_code, "client": client}
        if request.method == "POST":
            form = DeviceAuthorizationForm(request.POST)
            if form.is_valid():
                confirm = form.cleaned_data["action"] == "confirm"
                device_codes.confirm_or_deny_device_code(
                    authenticated_user(request), device_code, confirm=confirm
                )
                if confirm:
                    template_name = f"idp/oidc/device_authorization_confirmed.{account_settings.TEMPLATE_EXTENSION}"
                else:
                    template_name = f"idp/oidc/device_authorization_denied.{account_settings.TEMPLATE_EXTENSION}"
                return render(request, template_name, context)
        else:
            form = DeviceAuthorizationForm()
        context["autorization_url"] = (
            reverse("idp:oidc:device_authorization")
            + "?"
            + urlencode({"code": user_code})
        )

        return render(
            request,
            f"idp/oidc/device_authorization_confirm_form.{account_settings.TEMPLATE_EXTENSION}",
            context,
        )


device_authorization = DeviceAuthorizationView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_not_required, name="dispatch")
class TokenView(View):
    @transaction.atomic
    def post(self, request: HttpRequest) -> HttpResponse:
        try:
            get_validator_context().requested_resources = get_resources(request)
            if request.POST.get("grant_type") == Client.GrantType.DEVICE_CODE:
                return self._post_device_token(request)
            return self._create_token_response(request)
        except OAuth2Error as e:
            resp = JsonResponse(dict(e.twotuples))
            resp.status_code = e.status_code
            return resp

    def _create_token_response(
        self,
        request: HttpRequest,
        *,
        user: AbstractBaseUser | None = None,
        data: dict[str, Any] | None = None,
    ) -> HttpResponse:
        orequest = extract_params(request)
        oresponse = get_server(
            pre_token=[lambda orequest: self._pre_token(orequest, user, data)],
        ).create_token_response(*orequest)
        return convert_response(*oresponse)

    def _pre_token(
        self,
        orequest: Request,
        user: AbstractBaseUser | None,
        data: dict[str, Any] | None,
    ) -> None:
        if orequest.grant_type == Client.GrantType.DEVICE_CODE:
            assert user is not None  # nosec
            assert data is not None  # nosec
            if scope := data.get("scope"):
                orequest.scope = scope
            orequest.user = user

    def _post_device_token(self, request: HttpRequest) -> HttpResponse:
        try:
            user, data = device_codes.poll_device_code(request)
        except OAuth2Error as e:
            return HttpResponse(
                e.json, content_type="application/json", status=e.status_code
            )
        else:
            return self._create_token_response(request, user=user, data=data)


token = TokenView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_not_required, name="dispatch")
class UserInfoView(View):
    """
    The UserInfo Endpoint MUST support the use of the HTTP GET and HTTP POST methods
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        return self._respond(request)

    def post(self, request: HttpRequest) -> HttpResponse:
        return self._respond(request)

    def _respond(self, request: HttpRequest) -> HttpResponse:
        orequest = extract_params(request)
        try:
            oresponse = get_server().create_userinfo_response(*orequest)
            return convert_response(*oresponse)
        except OAuth2Error as e:
            return respond_json_error(request, e)


user_info = UserInfoView.as_view()


@method_decorator(login_not_required, name="dispatch")
class JwksView(View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        keys = []
        adapter = get_adapter()
        # Deliberately not filtering on ``did_activate``: keys whose
        # ``not_before`` still lies in the future are published ahead of time.
        # That way clients have already fetched and cached the next key before
        # it starts signing, avoiding a window where a freshly activated key
        # signs tokens that verifiers cannot yet validate.
        for key in adapter.list_private_keys(is_active=True):
            jwk, _ = jwkkit.load_jwk_from_pem(key.pem)
            keys.append(jwk)
        response = JsonResponse({"keys": keys})
        response["Access-Control-Allow-Origin"] = "*"
        response["Cache-Control"] = (
            f"max-age={adapter.get_jwks_cache_control()}, must-revalidate"
        )

        return response


jwks = JwksView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_not_required, name="dispatch")
class RevokeView(View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        orequest = extract_params(request)
        oresponse = get_server().create_revocation_response(*orequest)
        return convert_response(*oresponse)


revoke = RevokeView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_not_required, name="dispatch")
class IntrospectView(View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        ctx = get_validator_context()
        ctx.supported_auth_methods = app_settings.INTROSPECTION_AUTH_METHODS
        orequest = extract_params(request)
        try:
            # Throttle by source IP before client authentication runs, so that
            # unauthenticated and failed-authentication requests are bounded as
            # well. The per-client limit is consumed later, post-authentication.
            ratelimit.consume(
                request=request,
                app="allauth.idp.oidc",
                action="introspect_ip",
                raise_exception=True,
            )
            oresponse = get_server().create_introspect_response(*orequest)
        except RateLimited:
            return JsonResponse(
                {
                    "error": "temporarily_unavailable",
                    "error_description": "Too many requests.",
                },
                status=HTTPStatus.TOO_MANY_REQUESTS,
            )
        return convert_response(*oresponse)


introspect = IntrospectView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_not_required, name="dispatch")
class LogoutView(FormView):
    """
    https://openid.net/specs/openid-connect-rpinitiated-1_0.html
    """

    form_class = RPInitiatedLogoutForm
    template_name = f"idp/oidc/logout.{account_settings.TEMPLATE_EXTENSION}"

    def get(self, request: HttpRequest) -> HttpResponse:
        form = self.form_class(request.GET)
        if not form.is_valid():
            return self.form_invalid(form)
        if not self._must_ask(form):
            return self._handle(form, True)
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form: RPInitiatedLogoutForm) -> HttpResponse:
        return respond_html_error(self.request, form=form)

    def form_valid(self, form: RPInitiatedLogoutForm) -> HttpResponse:
        ask = self._must_ask(form)
        action = form.cleaned_data["action"]
        if ask:
            # If we're supposed to ask, we need to ensure this POST request does
            # NOT come from the RP, but from the actual user visitting the logout
            # page.
            csrf_token = self.request.POST.get("csrfmiddlewaretoken", "")
            if not csrf_token or not action:
                return self.render_to_response(self.get_context_data(form=form))
            csrf_resp = _enforce_csrf(self.request)
            if csrf_resp:
                return csrf_resp
            op_logout = action != "stay"
        else:
            op_logout = True
        return self._handle(form, op_logout)

    def _handle(self, form: RPInitiatedLogoutForm, op_logout: bool) -> HttpResponse:
        cleaned_data = form.cleaned_data
        flows.rp_initiated_logout(
            self.request,
            from_op=op_logout,
            client=cleaned_data["client"],
            post_logout_redirect_uri=cleaned_data["post_logout_redirect_uri"],
        )
        redirect_uri = cleaned_data["post_logout_redirect_uri"]
        if redirect_uri:
            state = cleaned_data["state"]
            if state:
                redirect_uri = add_query_params(redirect_uri, {"state": state})
        else:
            redirect_uri = get_account_adapter().get_logout_redirect_url(self.request)
        return _ClientHttpResponseRedirect(redirect_uri)

    def _must_ask(self, form: RPInitiatedLogoutForm) -> bool:
        """
        At the Logout Endpoint, the OP SHOULD ask the End-User whether to
        log out of the OP as well. Furthermore, the OP MUST ask the End-User
        this question if an id_token_hint was not provided or if the supplied ID
        Token does not belong to the current OP session with the RP and/or
        currently logged in End-User. If the End-User says "yes", then the OP
        MUST log out the End-User.
        """
        if self.request.user.is_anonymous:
            return False
        if app_settings.RP_INITIATED_LOGOUT_ASKS_FOR_OP_LOGOUT:
            return True
        id_token_hint = form.cleaned_data["id_token_hint"]
        sub = None
        if id_token_hint:
            sub = id_token_hint.get("sub")
        client = form.cleaned_data.get("client")
        if not id_token_hint or not client or not sub:
            return True
        user_hint = get_adapter().get_user_by_sub(client, sub)
        if not user_hint or (user_hint.pk != self.request.user.pk):
            return True
        return False


logout = LogoutView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_not_required, name="dispatch")
class ClientRegistrationView(View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        bearer_token, token, resp = self._authorize()
        if resp:
            return resp

        client_metadata = self._get_client_metadata()
        if client_metadata is None:
            return JsonResponse(
                {
                    "error": "invalid_client_metadata",
                    "error_description": "Invalid JSON data.",
                },
                status=HTTPStatus.BAD_REQUEST,
            )
        form = ClientRegistrationForm(data=client_metadata)
        if not form.is_valid():
            return self._form_invalid(form)
        return self._form_valid(
            form,
            client_metadata=client_metadata,
            bearer_token=bearer_token,
            token=token,
        )

    @transaction.atomic
    def _form_valid(
        self,
        form: ClientRegistrationForm,
        *,
        client_metadata: dict[str, Any],
        token: Token | None,
        bearer_token: str | None,
    ) -> HttpResponse:
        client = form.save(commit=False)
        client.data = {
            "dcr": True,
            "client_metadata": client_metadata,
        }
        secret = get_adapter().generate_client_secret()
        client.set_secret(secret)

        resp: HttpResponse | None
        usage, resp = self._ratelimit()
        if resp:
            return resp
        assert usage  # nosec
        resp = self._perform_custom_validation(
            client=client,
            client_metadata=client_metadata,
            token=token,
            bearer_token=bearer_token,
        )
        if resp:
            usage.rollback()
            return resp

        client.save()
        return JsonResponse(
            self._serialize_client(client, form, secret), status=HTTPStatus.CREATED
        )

    def _form_invalid(self, form: ClientRegistrationForm) -> JsonResponse:
        error_fields = list(form.errors.keys())
        if form.data and error_fields == ["redirect_uris"]:
            error = "invalid_redirect_uri"
        else:
            error = "invalid_client_metadata"

        if not form.data:
            error_description = "Invalid data received."
        else:
            error_description = "  ".join(
                [
                    f"'{field}': {' '.join([str(err) for err in errs])}"
                    for field, errs in form.errors.items()
                ]
            )
        return JsonResponse(
            {
                "error": error,
                "error_description": error_description,
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    def _authorize(self) -> tuple[str | None, Token | None, HttpResponse | None]:
        if not app_settings.DCR_REQUIRES_INITIAL_ACCESS_TOKEN:
            return None, None, None
        auth = self.request.headers.get("Authorization", "")
        scheme, _, bearer_token = auth.partition(" ")
        if scheme.lower() != "bearer" or not bearer_token:
            return None, None, self._respond_unauthorized()
        token = Token.objects.lookup(Token.Type.INITIAL_ACCESS_TOKEN, bearer_token)
        if not token:
            return None, None, self._respond_unauthorized()
        return bearer_token, token, None

    def _respond_unauthorized(self) -> HttpResponse:
        resp = HttpResponse(status=HTTPStatus.UNAUTHORIZED)
        resp["WWW-Authenticate"] = 'Bearer error="invalid_token"'
        return resp

    def _get_client_metadata(self) -> dict[str, Any] | None:
        try:
            data = json.loads(self.request.body)
        except (json.JSONDecodeError, ValueError):
            return None
        if not isinstance(data, dict):
            return None
        return data

    def _ratelimit(self) -> tuple[ratelimit.RateLimitUsage | None, JsonResponse | None]:
        usage = ratelimit.consume(
            request=self.request,
            app="allauth.idp.oidc",
            action="client_registration",
            raise_exception=False,
        )
        resp: JsonResponse | None = None
        if not usage:
            resp = JsonResponse(
                {
                    "error": "temporarily_unavailable",
                    "error_description": "Too many requests.",
                },
                status=HTTPStatus.TOO_MANY_REQUESTS,
            )
        return usage, resp

    def _perform_custom_validation(
        self,
        *,
        client: Client,
        client_metadata: dict[str, Any],
        token: Token | None,
        bearer_token: str | None,
    ) -> HttpResponse | None:
        try:
            get_adapter().validate_client_registration(
                client=client,
                client_metadata=client_metadata,
                token=token,
                bearer_token=bearer_token,
            )
        except ValidationError as e:
            return JsonResponse(
                {
                    "error": "invalid_client_metadata",
                    "error_description": str(e.message),
                },
                status=HTTPStatus.BAD_REQUEST,
            )
        except ImmediateHttpResponse as e:
            return e.response
        return None

    def _serialize_client(
        self, client: Client, form: ClientRegistrationForm, secret: str
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "client_id": client.id,
            "client_name": client.name,
            "token_endpoint_auth_method": form.cleaned_data[
                "token_endpoint_auth_method"
            ],
            "scope": " ".join(client.get_scopes()),
            "client_id_issued_at": int(client.created_at.timestamp()),
            "redirect_uris": client.get_redirect_uris(),
            "grant_types": client.get_grant_types(),
            "response_types": client.get_response_types(),
        }
        if client.type == Client.Type.CONFIDENTIAL:
            data.update(
                {
                    "client_secret": secret,
                    "client_secret_expires_at": 0,  # nosec
                }
            )
        return data


client_registration = ClientRegistrationView.as_view()
