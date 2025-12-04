from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.config import settings
from app.routers import auth, chat
from app.utils.security import login_required
from app.websocket import chatws


app = FastAPI()# FastAPI application instance

templates = Jinja2Templates(directory="app/templates")# Jinja2 templates for rendering HTML pages

app.add_middleware(
    # Session middleware for managing user sessions
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session_id",
    max_age=3600,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)# Authentication routes
app.include_router(chat.router)# Chat routes
app.include_router(chatws.router)# WebSocket chat routes

@app.get("/")
async def home():
    return RedirectResponse("/chat/rooms", status_code=302)