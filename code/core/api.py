# /code/core/api.py
from ninja import NinjaAPI
from ninja.security import HttpBearer
from ninja_simple_jwt.auth.views.api import mobile_auth_router

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        return token

api = NinjaAPI()
api.add_router("/auth/", mobile_auth_router)
apiAuth = AuthBearer()