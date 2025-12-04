from passlib.context import CryptContext
from fastapi import Request, HTTPException


pwd_context = CryptContext(
    # Password hashing context using bcrypt
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)
# Hash the plain password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
# Verify the plain password against the hashed password



def login_required(request: Request):
    # Check if user is logged in by verifying session data
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=302,
            detail="Redirect to login",
            headers={"Location": "/auth/login"},
        )
    return user_id

