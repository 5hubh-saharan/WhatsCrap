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
)

router = APIRouter(prefix="/chat")
# Chat router with URL prefix

templates = Jinja2Templates(directory="app/templates")
# Jinja2 templates for rendering HTML pages


@router.get("/rooms")
async def list_rooms(
    request: Request,
    db: AsyncSession = Depends(get_db), # Database session dependency
    user_id: str = Depends(login_required), # Ensure user is logged in
):
    """Display a list of all available chat rooms."""
    rooms = await get_all_rooms(db)
    # Retrieve all chat rooms from the database

    return templates.TemplateResponse(
        # Render the rooms page with the list of rooms and current username
        "rooms.html",
        {
            "request": request,
            "rooms": rooms,
            "username": request.session.get("username", "User") 
            # Get username from session or default to "User"
        },
    )


@router.get("/room/{room_id}")
async def open_room(
    request: Request, # Request object
    room_id: str, # Chat room ID from the URL path
    db: AsyncSession = Depends(get_db), # Database session dependency
    user_id: str = Depends(login_required), # Ensure user is logged in
):
    """Open a specific chat room and display its messages."""
    # Retrieve the chat room by ID
    room = await get_room(db, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")


    
    messages = await get_messages_for_room(db, room_id)
    # Retrieve messages for the chat room

   
    return templates.TemplateResponse( 
        # Render the chat room page with room details and messages
        "chatroom.html",
        {
            "request": request, # Request object
            "room": room, # Chat room details
            "messages": messages,  # List of messages in the room
            "username": request.session.get("username", "User") 
            # Get username from session or default to "User"
        },
    )


@router.post("/create-room") # Endpoint to create a new chat room
async def create_room(
    request: Request, # Request object
    name: str = Form(...), # Chat room name from form data
    db: AsyncSession = Depends(get_db), # Database session dependency
    user_id: str = Depends(login_required), # Ensure user is logged in
):
    """Create a new chat room."""
    try:
        # Create the chat room using the service function
        await create_room_service(db, name)
    except HTTPException as e:
        # If room creation fails, re-render the rooms page with an error message
        rooms = await get_all_rooms(db)
        return templates.TemplateResponse(
            "rooms.html",
            {
                "request": request,
                "rooms": rooms,
                "error": e.detail, # Error message to display
                "username": request.session.get("username", "User") 
            },
        )

    return RedirectResponse(url="/chat/rooms", status_code=302)
    # Redirect to the rooms list after successful creation