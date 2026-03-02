from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database import get_db
from app.models.models import User
from app.services.auth_service import verify_password, get_password_hash, create_access_token
from app.api.schemas import UserRegister, UserLogin, Token, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    result = await db.execute(select(User).where(User.username == user.username))
    existing_username = result.scalar_one_or_none()

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        subscription_tier="free"
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return UserResponse(
        id=str(db_user.id),
        username=db_user.username,
        email=db_user.email,
        subscription_tier=db_user.subscription_tier
    )


@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.username == user.username)
    )
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": db_user.username})

    return Token(access_token=access_token, token_type="bearer")


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    username: str = None,
    db: AsyncSession = Depends(get_db)
):
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    result = await db.execute(select(User).where(User.username == username))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=str(db_user.id),
        username=db_user.username,
        email=db_user.email,
        subscription_tier=db_user.subscription_tier
    )
