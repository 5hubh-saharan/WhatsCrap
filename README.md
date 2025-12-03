🚀 WhatsCrap — Real-Time Chat Application

A full-stack, production-ready chat application built with FastAPI, WebSockets, Async SQLAlchemy, Alembic, Neon PostgreSQL, and Docker, deployed on Render.

WhatsCrap allows users to register, log in, create chat rooms, and exchange real-time messages that persist in a database.

🌟 Features
🔐 Authentication

User registration & login

Secure password hashing (SHA256 + bcrypt)

Session-based authentication using cookies

💬 Real-Time Chat

WebSocket-powered messaging

Multiple chat rooms

Broadcast messages instantly to all connected users

View message history from the database

🗄️ Database & Migrations

PostgreSQL (Neon) as main database

Async SQLAlchemy ORM

Full Alembic migration system

Automatically creates tables on deploy via Docker

🌐 Deployment

Fully Dockerized

Production-ready server (Uvicorn)

Auto-migrates on deploy:

alembic upgrade head && uvicorn app.main:app

📦 Tech Stack
Backend

FastAPI

Starlette Sessions

SQLAlchemy 2.0 (async)

Alembic

asyncpg

Passlib (bcrypt)

Frontend

Jinja2 templates

HTML/CSS

Vanilla JS (WebSocket client)

Deployment

Docker

Render Web Services

Neon PostgreSQL

📁 Project Structure
app/
│
├── main.py                # FastAPI application setup
├── config.py              # Settings from .env (Pydantic)
│
├── database/
│   ├── base.py            # Declarative Base
│   ├── session.py         # Async engine + session
│
├── models/                # SQLAlchemy ORM models
│   ├── user.py
│   ├── chatroom.py
│   └── message.py
│
├── schemas/               # Pydantic schemas
│
├── routers/               # FastAPI route handlers
│   ├── auth.py
│   └── chat.py
│
├── services/              # Business logic
│   ├── auth_service.py
│   └── chat_service.py
│
├── websocket/
│   ├── chatws.py          # WebSocket endpoint
│   └── manager.py         # Connection manager
│
├── templates/             # HTML templates (Jinja2)
│
└── static/                # CSS / JS files

🛠️ Running Locally
1. Clone the repo
git clone https://github.com/5hubh-saharan/WhatsCrap.git
cd WhatsCrap

2. Set up a virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# or source venv/bin/activate on Linux/Mac

3. Install dependencies
pip install -r requirements.txt

4. Add your .env
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=your-secret-key

5. Run database migrations
alembic upgrade head

6. Start the app
uvicorn app.main:app --reload

🐳 Running with Docker (Production)

Build:

docker build -t whatscrap .


Run:

docker run -p 8000:8000 --env-file .env whatscrap

🔄 Deployment to Render

The service automatically runs:

alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000


This ensures:

DB tables always exist

Migrations run before app starts

🚧 Future Improvements

Planned features:

Private messaging (DMs)

User online/offline indicators

Typing indicators

Message timestamps formatting

Profile pictures

Responsive UI redesign

Push notifications

👤 Author

Shubhkarman Saharan
Backend Developer | FastAPI Enthusiast

❤️ Acknowledgements

FastAPI for the backend framework

Neon.tech for free cloud PostgreSQL

Render.com for hosting

SQLAlchemy & Alembic for database tooling