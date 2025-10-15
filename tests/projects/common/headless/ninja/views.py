from ninja import NinjaAPI

from allauth.headless.contrib.ninja.security import jwt_token_auth


api = NinjaAPI(urls_namespace="headless")


@api.get("/resource", auth=[jwt_token_auth])
def resource(request):
    data = {"resource": "ok"}
    if "userinfo" in request.GET:
        data["user_email"] = request.user.email
    return data
