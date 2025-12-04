"""from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# Import the SQLAlchemy asynchronous extension module
# create_async_engine: Creates an asynchronous database engine
# async_sessionmaker: Creates an asynchronous session factory
# AsyncSession: An asynchronous session class

from typing import AsyncGenerator
# Importing Asynchronous Generator Type Hints
# AsyncGenerator: The return type used to annotate asynchronous generators

from app.config import settings
# Import application configuration
# settings: Includes configuration information such as database URL



engine = create_async_engine(
    # Creating an Asynchronous Database Engine

    # This is the core component for connecting to the database, 
    # responsible for managing the connection pool and database communication.

    settings.DATABASE_URL,# Database connection URL, read from configuration file

    echo=False,
    # echo: Whether to output SQL statements to the console (for debugging)
    # False: Do not output SQL. Should be set to False in production environments.

    future=True,
    # future: Use SQLAlchemy 2.0 API
    # True: Enable 2.0 style API, recommended

    pool_size=20,
    # pool_size: The number of connections maintained in the connection pool
    # 20: Maintain 20 active connections simultaneously

    max_overflow=10,
    # max_overflow: The maximum number of connections that can be created beyond pool_size
    # 10: Allow up to 10 additional connections beyond the pool size

    pool_pre_ping=True,
    # pool_pre_ping: Enable connection health checks
    # True: Check connection health before using it to avoid stale connections

    pool_recycle=3600,
    # pool_recycle: Maximum lifetime of a connection in the pool (in seconds)
    # 3600: Recycle connections every hour to prevent timeout issues

)

AsyncSessionLocal = async_sessionmaker(
    # Creating an Asynchronous Session Factory
    # This factory is used to create database session instances.

    bind=engine,
    # bind: Bind the session factory to the database engine
    # engine: The asynchronous database engine created above

    expire_on_commit=False,
    # expire_on_commit: Whether to expire objects after commit
    # False: Do not expire objects after commit, keeping them accessible

    class_=AsyncSession,
    # class_: The session class to use
    # AsyncSession: Use the asynchronous session class provided by SQLAlchemy

    autocommit=False,
    # autocommit: Whether to enable autocommit mode
    # False: Disable autocommit, requiring explicit commits

    autoflush=False,
    # autoflush: Whether to enable autoflush mode
    # False: Disable autoflush, requiring explicit flushes

)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    # Asynchronous generator function: Obtaining a database session
    
    # This function is used by 
    # the FastAPI's Depends() dependency injection system

    # A new database session is created for each request 
    # and automatically closed after the request ends.

    """Asynchronous Database Session Generator

    This is a dependency injection function that is called on every request to obtain a database session.

    Using the FastAPI's Depends() system, it ensures that each request has an independent database session.

    Workflow:

    1. Create a new asynchronous session

    2. Hand the session over to the request handling function

    3. Automatically close the session and release the database connection after the request is completed

    4. Automatically roll back the transaction if an exception occurs

    Yields:

        AsyncSession: Database session object

    Raises:

        Exception: Any database operation exception will be rolled back and rethrown.
    """

    async with AsyncSessionLocal() as session:
        # Creating a session using an asynchronous context manager
        # AsyncSessionLocal() creates a new session instance

        try:
            yield session
            # Give the session to the caller
            # `yield` makes this function a generator, 
            # returning a session on each call.

        except Exception:
            await session.rollback()
            raise
            # Roll back the current transaction if any exception occurs.
            # Ensure data consistency and avoid partial commits.

        finally:
            await session.close()
            # This part will eventually be executed regardless of 
            # whether an exception occurs.
            # Close the session and release the database connection back to 
            # the connection pool.