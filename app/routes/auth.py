from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.auth import hash_password, verify_password

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    username = username.strip()
    error = None

    if not username:
        error = "Username must not be empty."
    elif len(username) > 64:
        error = "Username is too long (max 64 characters)."
    elif len(password) < 8:
        error = "Password must be at least 8 characters."
    elif len(password) > 1024:
        error = "Password is too long (max 1024 characters)."
    elif password != confirm_password:
        error = "Passwords do not match."

    if error:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": error}, status_code=400
        )

    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "Username already taken."},
                status_code=400,
            )
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password)),
        )

    return RedirectResponse(url="/login?registered=1", status_code=303)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, registered: str = ""):
    success = "Account created — please log in." if registered == "1" else None
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": None, "success": success}
    )


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE username = ?", (username.strip(),)
        ).fetchone()

    if row is None or not verify_password(password, row["password_hash"]):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password.", "success": None},
            status_code=401,
        )

    request.session["user_id"] = row["id"]
    request.session["username"] = username.strip()
    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
