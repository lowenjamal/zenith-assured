from fastapi import APIRouter, Depends
from router.general_route import route

router = APIRouter()


router.include_router(
    route.router,
    prefix="",
    tags=["General Route"],
    responses={418: {"description": "This is General Route"}}
)