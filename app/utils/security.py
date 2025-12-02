from passlib.context import CryptContext

from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse


pwd_context = CryptContext(
    schemas = ["bcrypt"],
    depricated = "auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> str:
    return pwd_context.verify(plain_password, hashed_password)


def login_required(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(status_code=302, detail="Redirect", headers={"Location": "/auth/login"})

    return user_id
