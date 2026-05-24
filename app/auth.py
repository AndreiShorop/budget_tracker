import base64
import hashlib
import os
import sys
from typing import Optional

import bcrypt
from fastapi import Request
from fastapi.responses import RedirectResponse


def _prepare(plain: str) -> bytes:
    """SHA-256 pre-hash so bcrypt never sees more than 44 bytes.

    bcrypt truncates at 72 bytes, meaning two passwords that share the first
    72 bytes would be treated as identical.  Pre-hashing with SHA-256 avoids
    that truncation while still correctly distinguishing every unique password.
    """
    return base64.b64encode(hashlib.sha256(plain.encode()).digest())

# Warn loudly at startup if the secret is not set
SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    print(
        "WARNING: SECRET_KEY env var is not set. "
        "Using an insecure default — do NOT use this in production.",
        file=sys.stderr,
    )
    SECRET_KEY = "change-me-in-production-please"


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(_prepare(plain), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_prepare(plain), hashed.encode())


def get_current_user(request: Request) -> Optional[dict]:
    """Return the session user dict or None."""
    user_id = request.session.get("user_id")
    username = request.session.get("username")
    if user_id and username:
        return {"id": user_id, "username": username}
    return None


def require_login(request: Request):
    """FastAPI dependency — redirects to /login if not authenticated."""
    user = get_current_user(request)
    if user is None:
        raise _redirect_to_login()
    return user


def _redirect_to_login():
    from fastapi import HTTPException  # local import to avoid circular

    # We can't raise a RedirectResponse from a dependency directly, so we
    # use a plain HTTPException and catch it in a custom handler in main.py.
    # However, FastAPI does allow raising Response objects via HTTPException
    # workaround — the cleanest approach is to just raise the redirect.
    return RedirectResponse(url="/login", status_code=302)
