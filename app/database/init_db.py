import asyncio
from app.database.session import engine
from app.database.base import Base
from app.models import *  

async def init_db():
    async with engine.begin() as conn:
        print("Creating tables in Neon PostgreSQL...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
