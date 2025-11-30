# 💬 WhatsCrap
A modern, lightweight chat application built with **FastAPI**, **Neon PostgreSQL**, **WebSockets**, and **HTML/CSS**.

WhatsCrap is a learning project designed to explore:
- Backend development with FastAPI
- Session-based authentication (Flask-style)
- WebSocket real-time communication
- Database modeling with async SQLAlchemy
- Clean folder structure and modular architecture

> ⚠️ This project is in early development.  
> Only the initial folder structure and setup are complete — core features are being implemented.

---

## 🚀 Features (Planned)
- 🔐 Username + Password authentication (session cookies)
- 💬 Multiple chat rooms (like Discord channels)
- 🧵 Real-time messaging over WebSockets
- 🗄️ Chat history stored in database (with per-room limit)
- 🎨 Simple HTML/CSS interface (no frameworks)
- 🧰 Fully asynchronous backend using async SQLAlchemy
- 🗂️ Clean project structure (routers, services, models, templates)
- 🐳 Docker support (planned)

---

## 🏗️ Technology Stack

### **Backend**
- FastAPI
- Starlette (Session middleware, WebSocket handling)
- SQLAlchemy (async)
- asyncpg (PostgreSQL driver)
- passlib[bcrypt] (password hashing)

### **Database**
- Neon PostgreSQL (cloud-hosted, serverless)

### **Frontend**
- Jinja2 Templates
- HTML5 / CSS3
- Vanilla JavaScript (only for WebSocket events)

### **Tools**
- Alembic (migrations)
- Uvicorn (ASGI server)
- python-dotenv (environment config)

---

## 📁 Project Structure

WhatsCrap/
└── app/
├── main.py
├── config.py
├── database/
├── models/
├── schemas/
├── routers/
├── services/
├── utils/
├── websocket/
├── templates/
└── static/


This modular layout keeps the project clean and scalable as more features are added.

---

## ⚙️ Setup (WIP)
Once development progresses, setup instructions will include:

pip install -r requirements.txt
uvicorn app.main:app --reload


Database configuration will be stored in your `.env` file.

---

## 📚 Current Progress
- [x] Folder structure created  
- [x] Basic wiring planned (authentication, chat logic, WebSockets)
- [ ] Implement authentication system  
- [ ] Implement chat room database models  
- [ ] Implement WebSocket manager  
- [ ] Render chat UI  
- [ ] Docker deployment setup  

---

## 🧑‍💻 Purpose of This Project
WhatsCrap is built as part of a personal learning initiative to understand:

- Backend architecture  
- Real-time communication  
- Web application security  
- Industry-standard code organization  
- Cloud database integration  

This is not intended for production use (yet).

---

## 🛑 Legal Disclaimer
**WhatsCrap is an educational project.**  
It is **not affiliated with, endorsed by, or connected to WhatsApp™ or Meta™ in any way.**  
The name “WhatsCrap” is a parody and is used for academic and personal learning purposes only.  
All trademarks and copyrights remain the property of their respective owners.

---

## 🤝 Contributing
Since this is a personal learning project, contributions are currently closed.  
Feedback and suggestions through Issues are welcome.

---

## 📜 License
This repository uses GitHub’s default public license.  

---

## ⭐ Acknowledgments
- The FastAPI documentation  
- SQLAlchemy async tutorials  
- Neon documentation for PostgreSQL  
- Chat app design inspirations (Discord, Slack)

---

## 📝 Roadmap
A more detailed roadmap will be added once core features are implemented.

Stay tuned!

