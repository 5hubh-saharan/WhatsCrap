from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers import auth, chat
from app.utils.security import login_required
from app.websocket import chatws


app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session_id",
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(chatws.router)



@app.get("/")
async def home(request: Request, user_id: str = Depends(login_required)):
    return templates.TemplateResponse("rooms.html", {"request": request})
