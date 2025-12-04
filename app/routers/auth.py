from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services.auth_service import create_user, authenticate_user

router = APIRouter(prefix="/auth")
# Authentication router with URL prefix

templates = Jinja2Templates(directory="app/templates")
# Jinja2 templates for rendering HTML pages


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Render the user registration page.""" 
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register_user(
    request: Request,
    username: str = Form(...), # Username from form data

    password: str = Form(...), # Password from form data

    db: AsyncSession = Depends(get_db),# Database session dependency
):
    """Handle user registration form submission."""
    try:
        # Create a new user (validation is handled by create_user function)
        await create_user(db, username, password)
        
        # Redirect to login page after successful registration
        return RedirectResponse(
            url="/auth/login", 
            status_code=302
        )
    except Exception as e:
        # Extract error message from exception
        error_message = str(e.detail) if hasattr(e, 'detail') else "Registration failed"
        
        # Return registration page with error message and pre-filled username
        return templates.TemplateResponse(
            "register.html", 
            {
                "request": request, 
                "error": error_message,
                "username": username  # Keep the entered username for better UX
            }
        )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render the user login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login_user(
    request: Request,
    username: str = Form(...),# Username from form data

    password: str = Form(...),# Password from form data

    db: AsyncSession = Depends(get_db),# Database session dependency
):
    """Handle user login form submission."""
    user = await authenticate_user(db, username, password)
    # Authenticate user credentials

    if not user:
        # Return login page with error if authentication fails
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request, 
                "error": "Invalid username or password",
                "username": username  # Keep the entered username for better UX
            }
        )

    # Store user info in session upon successful login
    request.session["user_id"] = str(user.id)
    request.session["username"] = user.username
    
    # Redirect to home page after successful login
    return RedirectResponse(url="/", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    """Handle user logout by clearing session data."""
    request.session.clear()# Clear all session data
    return RedirectResponse(url="/auth/login", status_code=302)