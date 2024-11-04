from fastapi import APIRouter, Depends
from .user_routes.auth import index
from .user_routes.profile import profile
from .user_routes.account import account
from .user_routes.transactions import transactions
from .user_routes.manual_trade import trader
from .user_routes.verify_and_reset import verify_an_reset_route
from dependencies import get_token_header
from .user_routes.verify_document import verify_document_route

router = APIRouter()

router.include_router(
    index.router,
    prefix="/auth",
    tags=["auth"],
    responses={418: {"description": "This is Auth"}}
)

router.include_router(
    profile.router,
    prefix="/profile",
    tags=["profile"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not Found"}}
)

router.include_router(
    account.router,
    prefix="/account",
    tags=["account"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not Found"}}
)

router.include_router(
    transactions.router,
    prefix="/transaction",
    tags=["transactions"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not Found"}}
)

router.include_router(
    trader.router,
    prefix="/trader",
    tags=["trader"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not Found"}}
)

router.include_router(
    verify_an_reset_route.router,
    prefix="/verify-and-reset",
    tags=["verify", "reset"],
    responses={404: {"description": "Not Found"}}
)

router.include_router(
    verify_document_route.router,
    prefix="/verify-document",
    tags=["id verification", "verify"],
    responses={404: {"description": "Not Found"}}
)