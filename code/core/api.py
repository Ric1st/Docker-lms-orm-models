# /code/core/api.py
from ninja_simple_jwt.auth.views.api import mobile_auth_router

api = NinjaAPI()
api.add_router("/auth/", mobile_auth_router)
apiAuth = HttpJwtAuth()