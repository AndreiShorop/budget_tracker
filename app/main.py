from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.auth import SECRET_KEY
from app.database import init_db
from app.routes import auth as auth_router
from app.routes import transactions as tx_router
from app.routes import pages as pages_router

app = FastAPI(title="Budget Tracker")

# Session middleware must be added before routers are used
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="budget_session",
    same_site="lax",
    https_only=False,  # set True behind HTTPS in production
    max_age=86400 * 7,  # 7 days
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages_router.router)
app.include_router(auth_router.router)
app.include_router(tx_router.router)


@app.on_event("startup")
async def startup():
    init_db()
