from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.user_schema import UserCreate
from app.services.auth_service import create_user, authenticate_user


router = APIRouter(prefix="/auth")
templates = Jinja2Templates(directory="app/templates")


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
    try:
        # 创建用户数据对象（验证由create_user函数完成）
        await create_user(db, username, password)
        
        # 注册成功，重定向到登录页面
        return RedirectResponse(
            url="/auth/login", 
            status_code=302
        )
    except Exception as e:
        # 获取错误信息
        error_message = str(e.detail) if hasattr(e, 'detail') else "Registration failed"
        
        # 返回注册页面并显示错误
        return templates.TemplateResponse(
            "register.html", 
            {
                "request": request, 
                "error": error_message,
                "username": username  # 保留已输入的用户名
            }
        )


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
    user = await authenticate_user(db, username, password)

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request, 
                "error": "Invalid username or password",
                "username": username  # 保留已输入的用户名
            }
        )

    # 设置session
    request.session["user_id"] = str(user.id)
    request.session["username"] = user.username
    
    return RedirectResponse(url="/", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=302)