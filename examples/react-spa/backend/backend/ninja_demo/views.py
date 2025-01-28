from ninja import NinjaAPI
from ninja.security import django_auth

from allauth.headless.contrib.ninja.security import x_session_token_auth


api = NinjaAPI()


@api.get("/add", auth=[django_auth, x_session_token_auth])
def add(request, x: float, y: float):
    return {"result": x + y}
