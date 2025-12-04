from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.user import User
from app.utils.security import hash_password, verify_password


async def create_user(db: AsyncSession, username: str, password: str) -> User:
    """
    创建新用户（包含完整的验证逻辑）
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 密码
    
    Returns:
        创建的User对象
    
    Raises:
        HTTPException: 验证失败时抛出错误
    """
    # 1. 用户名验证
    if not username or len(username.strip()) == 0:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    
    if len(username) > 100:
        raise HTTPException(status_code=400, detail="Username too long (max 100 characters)")
    
    # 2. 密码验证
    if not password:
        raise HTTPException(status_code=400, detail="Password cannot be empty")
    
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    if len(password) > 128:
        raise HTTPException(status_code=400, detail="Password too long (max 128 characters)")
    
    # 3. 检查用户名是否已存在
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail=f"Username '{username}' already exists")
    
    # 4. 创建用户
    hashed_pw = hash_password(password)
    user = User(username=username, password=hashed_pw)

    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        # 再次检查是否是用户名重复的错误
        raise HTTPException(status_code=400, detail=f"Username '{username}' already exists")
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while creating user"
        )


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    """
    验证用户凭据
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 密码
    
    Returns:
        如果验证成功返回User对象，否则返回None
    """
    # 输入验证
    if not username or not password:
        return None
    
    try:
        statement = select(User).where(User.username == username)
        result = await db.execute(statement)
        user = result.scalars().first()

        if user and verify_password(password, user.password):
            return user

        return None
    except Exception:
        return None


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """
    根据ID获取用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
    
    Returns:
        User对象或None
    """
    try:
        import uuid
        user_uuid = uuid.UUID(user_id)
        stmt = select(User).where(User.id == user_uuid)
        result = await db.execute(stmt)
        return result.scalars().first()
    except (ValueError, AttributeError):
        # 无效的UUID格式或user_id为空
        return None
    except Exception:
        return None


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """
    根据用户名获取用户
    
    Args:
        db: 数据库会话
        username: 用户名
    
    Returns:
        User对象或None
    """
    try:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalars().first()
    except Exception:
        return None