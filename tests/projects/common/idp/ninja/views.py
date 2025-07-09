from ninja import NinjaAPI

from allauth.idp.oidc.contrib.ninja.security import TokenAuth


api = NinjaAPI()


@api.get("/resource", auth=[TokenAuth(scope=["view-resource"])])
def resource(request):
    return {"resource": "ok", "user_email": request.user.email}
