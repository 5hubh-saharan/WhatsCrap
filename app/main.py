from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

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

app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(chatws.router)



@app.get("/")
async def home():
    return RedirectResponse("/chat/rooms", status_code=302)
