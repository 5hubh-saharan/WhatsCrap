import asyncio
# asyncio: Python's asynchronous I/O framework for handling concurrent operations.
from app.database.session import engine
# Database engine, used for connecting to and manipulating databases
from app.database.base import Base
# The declarative base class for SQLAlchemy, the foundation of all models.
from app.models import *
# Import all models and ensure they are registered in Base.metadata  

async def init_db():
    """Asynchronously initialize the database and create all defined tables.

    This function will:

    1. Create a connection using an asynchronous database engine.

    2. Perform SQLAlchemy table creation operations synchronously.

    3. Print progress information of the creation process.

    Note: In production environments, Alembic is typically used for database migrations.

    This function is primarily for development environments or quick setups."""
    async with engine.begin() as conn:
        print("Creating tables in Neon PostgreSQL...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
