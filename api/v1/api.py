from fastapi import APIRouter

from api.v1.endpoints import users, fund, admin, api_key

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(fund.router, prefix="/fund", tags=["fund"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(api_key.router, prefix="/api-keys", tags=["api-keys"]) 