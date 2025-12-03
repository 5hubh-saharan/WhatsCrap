# app/routers/chat.py

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.security import login_required
from app.services.chat_service import (
    get_all_rooms,
    get_room,
    create_room_service,
    get_messages_for_room,
    create_message,
)

router = APIRouter(prefix="/chat")
templates = Jinja2Templates(directory="app/templates")


@router.get("/rooms")
async def list_rooms(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(login_required),
):
    rooms = await get_all_rooms(db)
    return templates.TemplateResponse(
        "rooms.html",
        {"request": request, "rooms": rooms},
    )


@router.get("/room/{room_id}")
async def open_room(
    request: Request,
    room_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(login_required),
):
    room = await get_room(db, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    messages = await get_messages_for_room(db, room_id)
    return templates.TemplateResponse(
        "chatroom.html",
        {"request": request, "room": room, "messages": messages},
    )


@router.post("/create-room")
async def create_room(
    request: Request,
    name: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(login_required),
):
    try:
        await create_room_service(db, name)
    except HTTPException as e:
        rooms = await get_all_rooms(db)
        return templates.TemplateResponse(
            "rooms.html",
            {"request": request, "rooms": rooms, "error": e.detail},
        )

    return RedirectResponse(url="/chat/rooms", status_code=302)


@router.post("/send-message/{room_id}")
async def send_message(
    request: Request,
    room_id: str,
    content: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(login_required),
):
    await create_message(db, room_id, user_id, content)
    return RedirectResponse(url=f"/chat/room/{room_id}", status_code=302)
