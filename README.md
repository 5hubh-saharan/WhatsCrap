# 🗨️ WhatsCrap

A real-time chat application built with **FastAPI**, **WebSockets**, **SQLAlchemy (async)**, **Alembic**, and **PostgreSQL**, fully containerized with **Docker** and deployed on **Render**.

WhatsCrap allows users to register, log in, create chat rooms, and exchange messages instantly — with all messages stored persistently in a PostgreSQL database.

---

## 🚀 Features

### 🔐 User Authentication

* Register and log in securely
* Passwords hashed using SHA-256 + bcrypt through Passlib
* Session-based authentication using cookies

### 💬 Real-Time Messaging

* Multiple chat rooms
* WebSocket communication
* Messages broadcast instantly to all connected users
* Message history saved in PostgreSQL and loaded on reconnect

### 🗄️ Modern Database Layer

* PostgreSQL (Neon)
* Async SQLAlchemy ORM (2.0 style)
* Alembic migrations for versioned schema changes
* Automatic migrations in production (Docker CMD)

### 🌐 Production Deployment

* Dockerized FastAPI app
* Automatic database migrations on container startup
* Live deployment on Render

---

## 🧰 Tech Stack

**Backend:**

* FastAPI
* Starlette Sessions
* SQLAlchemy 2.0 (async)
* Alembic
* asyncpg
* Passlib (bcrypt)

**Frontend:**

* Jinja2 Templates
* HTML + CSS
* Vanilla JavaScript (WebSocket client)

**Infrastructure:**

* Docker
* Render Web Service
* Neon PostgreSQL

---

## 📁 Project Structure

```
app/
│
├── main.py                # FastAPI app + middleware + routers
├── config.py              # App settings (reads from .env)
│
├── database/
│   ├── base.py            # Declarative Base
│   ├── session.py         # Async DB session + engine
│
├── models/                # SQLAlchemy ORM models
│   ├── user.py
│   ├── chatroom.py
│   └── message.py
│
├── schemas/               # Pydantic request/response models
│
├── routers/               # API + HTML routes
│   ├── auth.py
│   └── chat.py
│
├── services/              # Business logic (auth, chat, messages)
│   ├── auth_service.py
│   └── chat_service.py
│
├── websocket/             # WebSocket manager + endpoint
│   ├── manager.py
│   └── chatws.py
│
├── templates/             # HTML views
│
└── static/                # CSS / JS
```

---

## 🛠️ Running Locally

### 1. Clone the repo

```bash
git clone https://github.com/5hubh-saharan/WhatsCrap.git
cd WhatsCrap
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\\Scripts\\activate   # Windows
# or: source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>/<db>
SECRET_KEY=your-secret-key
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the development server

```bash
uvicorn app.main:app --reload
```

App will be available at: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🐳 Running with Docker

### Build image

```bash
docker build -t whatscrap .
```

### Run container

```bash
docker run -p 8000:8000 --env-file .env whatscrap
```

---

## 🔄 Deployment on Render

Render automatically runs on startup:

```sh
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

This ensures:

* All migrations apply successfully
* Tables are created before the app starts

---

## 🚧 Future Improvements

* Direct messaging (DMs)
* Online/offline user indicators
* Typing indicators
* Profile pictures
* Message timestamps formatting
* Fully responsive UI
* Push notifications

---

## 👤 Author

**Shubhkarman Saharan**

Backend Developer | FastAPI Enthusiast

---

## ❤️ Acknowledgements

* FastAPI
* SQLAlchemy
* Alembic
* asyncpg
* Neon PostgreSQL
* Render.com
