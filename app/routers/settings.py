# app/routers/settings.py
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.security import login_required
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings")
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    user_id: str = Depends(login_required)
):
    """显示设置页面"""
    # 从 session 中获取用户设置，如果没有则使用默认设置
    user_settings = request.session.get("user_settings", SettingsService.get_default_settings())
    
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "settings": user_settings,
            "username": request.session.get("username", "User")
        }
    )

@router.post("/save")
async def save_settings(
    request: Request,
    theme_color: str = Form(...),
    my_bubble_color: str = Form(...),
    other_bubble_color: str = Form(...),
    room_display: str = Form(...),
    user_id: str = Depends(login_required)
):
    """保存用户设置"""
    # 验证颜色格式
    def is_valid_color(color):
        import re
        hex_color_pattern = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')
        return bool(hex_color_pattern.match(color))
    
    # 验证颜色
    colors_to_validate = [theme_color, my_bubble_color, other_bubble_color]
    if not all(is_valid_color(color) for color in colors_to_validate):
        current_settings = request.session.get("user_settings", SettingsService.get_default_settings())
        return templates.TemplateResponse(
            "settings.html",
            {
                "request": request,
                "settings": current_settings,
                "error": "Invalid color format. Colors must be in hex format (e.g., #FF0000).",
                "username": request.session.get("username", "User")
            }
        )
    
    # 验证 room_display
    if room_display not in ["bubble", "grid"]:
        current_settings = request.session.get("user_settings", SettingsService.get_default_settings())
        return templates.TemplateResponse(
            "settings.html",
            {
                "request": request,
                "settings": current_settings,
                "error": "Invalid room display option. Must be 'bubble' or 'grid'.",
                "username": request.session.get("username", "User")
            }
        )
    
    # 保存设置到 session
    request.session["user_settings"] = {
        "theme_color": theme_color,
        "my_bubble_color": my_bubble_color,
        "other_bubble_color": other_bubble_color,
        "room_display": room_display
    }
    
    # 同时更新背景颜色，保持与现有系统的兼容性
    request.session["app_background_color"] = theme_color
    
    # 重定向回设置页面并显示成功消息
    return RedirectResponse(
        url="/settings?success=true",
        status_code=302
    )

@router.get("/reset")
async def reset_settings(
    request: Request,
    user_id: str = Depends(login_required)
):
    """重置设置为默认值"""
    default_settings = SettingsService.get_default_settings()
    request.session["user_settings"] = default_settings
    request.session["app_background_color"] = default_settings["theme_color"]
    
    # 重定向回设置页面
    return RedirectResponse(
        url="/settings?success=true&message=Settings%20reset%20to%20default",
        status_code=302
    )

@router.get("/api/get")
async def get_settings(
    request: Request,
    user_id: str = Depends(login_required)
):
    """获取用户设置（用于前端 API 调用）"""
    settings = request.session.get("user_settings", SettingsService.get_default_settings())
    return {
        "success": True,
        "settings": settings
    }

@router.post("/api/update")
async def update_settings_api(
    request: Request,
    user_id: str = Depends(login_required)
):
    """通过 API 更新用户设置"""
    try:
        data = await request.json()
        settings = request.session.get("user_settings", SettingsService.get_default_settings())
        
        # 合并设置
        updated_settings = {**settings, **data}
        
        # 验证设置
        is_valid, message = SettingsService.validate_settings(updated_settings)
        if not is_valid:
            return {"success": False, "error": message}
        
        # 保存到 session
        request.session["user_settings"] = updated_settings
        
        # 如果更新了主题颜色，也更新背景颜色
        if "theme_color" in data:
            request.session["app_background_color"] = data["theme_color"]
        
        return {"success": True, "settings": updated_settings}
    except Exception as e:
        return {"success": False, "error": str(e)}