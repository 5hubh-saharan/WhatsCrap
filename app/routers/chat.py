from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.security import login_required
from app.services.chat_service import chat_service


router = APIRouter(prefix="/chat")
templates = Jinja2Templates(directory="app/templates")

@router.get("/rooms")
async def list_rooms(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(login_required)
):
    rooms = await chat_service.get_all_rooms(db)
    return templates.TemplateResponse("rooms.html", {"request": request, "rooms": rooms})

@router.get("/room/{room_id}")
async def open_room(
    request: Request,
    room_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(login_required)
):
    room = await chat_service.get_room(db, room_id)
    return templates.TemplateResponse("chatroom.html", {"request": request, "rooms": room})