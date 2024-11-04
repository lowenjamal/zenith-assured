from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
import secrets
from fastapi.middleware.cors import CORSMiddleware
from router import users_route, admin_routes, general_routes
from dependencies import check_if_user_admin, can_use_route
from database import SessionLocal
from auto_tasks.jobs import scheduler


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


scheduler.start()

app = FastAPI(
    title="FinnoVent Trader Backend API",
    description="Trader Framework",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

security = HTTPBasic()

origins = [
    "http://localhost:3000",
    "https://trader.atlaswavestrader.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Security for Docs and Re-docs and openjson url
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "finno-admin")
    correct_password = secrets.compare_digest(credentials.password, "MichaelandJamalSoft")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/docs")
async def get_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="FinnoVent Trader App Docs")


@app.get("/redoc")
async def get_redocs(username: str = Depends(get_current_username)):
    return get_redoc_html(openapi_url="/openapi.json", title="FinnoVent Trader App Redoc")


@app.get("/openapi.json")
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title="Finno Trader App Documentation", version="0.1.0", routes=app.routes)


# User Routes
app.include_router(
    users_route.router,
    prefix="/user",
    tags=["user"],
    responses={418: {"description": "This is User"}}
)


# Admin Routes
app.include_router(
    admin_routes.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(check_if_user_admin)],
    responses={418: {"description": "This is Admin"}}
)

# General Routes
app.include_router(
    general_routes.router,
    prefix="/general-route",
    tags=["General Route"],
    dependencies=[Depends(can_use_route)],
    responses={418: {"description": "This is General Route"}}
)

@app.on_event("startup")
async def auto_trade_bot():
    background_tasks = BackgroundTasks()
    background_tasks.add_task(func=scheduler)

@app.get("/")
async def root():
    return {"message": "Hello World"}
