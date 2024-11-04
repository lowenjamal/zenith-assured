from fastapi import APIRouter, Depends
from .admin_route.asset_pair import asset
from .admin_route.user_activities import user
from .admin_route.finance_details import finance_details
from .admin_route.crm import crm_route
from .admin_route.super_admin import super_admin_routes
from dependencies import check_if_super_admin

router = APIRouter()

router.include_router(
    asset.router,
    prefix="/asset",
    tags=["asset"],
    responses={418: {"description": "This is Auth"}}
)

router.include_router(
    user.router,
    prefix="/user",
    tags=["admin user activities"],
    responses={418: {"description": "This is User Activities"}}
)

router.include_router(
    crm_route.router,
    prefix="/crm",
    tags=["crm"],
    responses={418: {"description": "This is CRM Activities"}}
)

router.include_router(
    finance_details.router,
    prefix="/finance-details",
    tags=["finance"],
    dependencies=[Depends(check_if_super_admin)],
    responses={418: {"description": "This is CRM Activities"}}
)

router.include_router(
    super_admin_routes.router,
    prefix="/super-admin",
    tags=["super admin"],
    dependencies=[Depends(check_if_super_admin)],
    responses={418: {"description": "This is CRM Activities"}}
)
