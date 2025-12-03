from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.utils.security import hash_password, verify_password


async def create_user(db: AsyncSession, username: str, password: str) -> User:
    hashed_pw = hash_password(password)
    user = User(username=username, password=hashed_pw)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    statement = select(User).where(User.username == username)
    result = await db.execute(statement)
    user = result.scalars().first()

    if user and verify_password(password, user.password):
        return user

    return None
