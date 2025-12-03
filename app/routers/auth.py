from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.user_schema import UserCreate, UserLogin
from app.services.auth_service import create_user, authenticate_user


router = APIRouter(prefix="/auth")
templates = Jinja2Templates(directory="app/templates")


# Register = get, post

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    if len(password) < 6:
        return templates.TemplateResponse("register.html", {
            "request": request, 
            "error": "Password must be at least 6 characters"
        })
    
    try:
        user_data = UserCreate(username=username, password=password)
        await create_user(db, user_data.username, user_data.password)
        return RedirectResponse(url="/auth/login", status_code=302)
    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Username already exists"
        })


# Login = get, post

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    login_data = UserLogin(username=username, password=password)
    user = await authenticate_user(db, login_data.username, login_data.password)

    if not user:
        return templates.TemplateResponse("login.html",{"request": request, "error": "Invalid username or password"})

    
    request.session["user_id"] = str(user.id)
    return RedirectResponse(url="/", status_code=302)


# Logout

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=302)