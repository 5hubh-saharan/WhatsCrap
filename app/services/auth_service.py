from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.user import User
from app.utils.security import hash_password, verify_password


async def create_user(
        db: AsyncSession, username: str, password: str) -> User:
    """
    Create a new user (including complete authentication logic)

    Args:

        db: Database session

        username: Username

        password: Password

    Returns:

        The created User object

    Raises:

        HTTPException: Throws an error if authentication fails
    """
    # 1. Username verification
    if not username or len(username.strip()) == 0:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    
    if len(username) > 100:
        raise HTTPException(
            status_code=400, detail="Username too long (max 100 characters)")
    
    # 2. Password verification
    if not password:
        raise HTTPException(status_code=400, detail="Password cannot be empty")
    # Password length checks
    
    if len(password) < 6:
        raise HTTPException(
            status_code=400, detail="Password must be at least 6 characters")
    # Min length check
    
    if len(password) > 128:
        raise HTTPException(
            status_code=400, detail="Password too long (max 128 characters)")
    # Max length check
    
    # 3. Check if the username already exists.
    stmt = select(User).where(User.username == username)
    # Query to find existing user by username

    result = await db.execute(stmt)
    # Execute the query


    if result.scalars().first():
        raise HTTPException(
            status_code=400, detail=f"Username '{username}' already exists")
    # Username already taken
    
    # 4. Create a user
    hashed_pw = hash_password(password)
    user = User(username=username, password=hashed_pw)

    try:
        db.add(user) # Add the new user to the session
        await db.commit() # Commit the transaction to save the user
        await db.refresh(user) # Refresh the instance to get updated data from the DB
        return user
    except IntegrityError:
        await db.rollback()
        # Double-check if it's a duplicate username error.
        raise HTTPException(
            status_code=400, detail=f"Username '{username}' already exists")
            # Integrity error likely due to duplicate username

    except Exception as e:
        await db.rollback() # Rollback on any other exception
        raise HTTPException(
            status_code=500,
            detail="Internal server error while creating user"
        ) # General error


async def authenticate_user(
        db: AsyncSession, username: str, password: str) -> User | None:
    """
    Verify user credentials

    Args:

        db: Database session

        username: Username

        password: Password

    Returns:

        Returns a User object if authentication is successful, otherwise returns None
    """
    # Input Validation
    if not username or not password:
        return None
        # Missing username or password
    
    try:
        statement = select(User).where(User.username == username)
        # Query to find user by username

        result = await db.execute(statement)
        # Execute the query

        user = result.scalars().first()
        # Get the first matching user

        if user and verify_password(password, user.password):
            return user
            # Password matches, return the user

        return None
    except Exception:
        return None


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """
    Retrieve User by ID

    Args:

        db: Database session

        user_id: User ID

    Returns: 
        User object or None
    """
    try:
        import uuid
        user_uuid = uuid.UUID(user_id)
        stmt = select(User).where(User.id == user_uuid)
        result = await db.execute(stmt)
        return result.scalars().first()
    except (ValueError, AttributeError):
        # Invalid UUID format or empty user_id
        return None
    except Exception:
        return None


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """
    Retrieve User by Username

    Args:

        db: Database session

        username: Username

    Returns: 
        User object or None
    """
    try:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalars().first()
    except Exception:
        return None