import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends
from jose import jwt
from dotenv import load_dotenv
from ..model.User_model import User
from ..schema.user_schema import UserCreate, UserLogin
from ..database.db import get_db

load_dotenv()

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE = 2


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def hash_password(self, password: str) -> str:
        hash_password = pwd.hash(password)
        return hash_password

    async def verify_password(self, plain_password: str, hash_password: str):
        return pwd.verify(plain_password, hash_password)

    async def get_user_by_email(self, email) -> dict:
        check_user = await self.db.execute(select(User).where(User.email == email))
        return check_user.scalar_one_or_none()

    async def create_token(self, data: dict) -> dict:
        to_encode = data.copy()
        expires_in = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE)
        to_encode.update({"exp": expires_in, "type": "access"})
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return {
            "access_token" : token,
            "expires_in": ACCESS_TOKEN_EXPIRE * 3600
        }

    async def create_user(self, payload: UserCreate):
        check_user = await self.get_user_by_email(payload.email)
        if check_user:
            raise HTTPException(
                status_code=409,
                detail="User already exist"
            )
        try:
            hash_password = await self.hash_password(payload.password)
            new_user = User(
                username = payload.username,
                email = payload.email,
                password = hash_password,
                role = payload.role,
            )
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    
    async def login_user(self, payload: UserLogin):
        user = await self.get_user_by_email(payload.email)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        is_valid = await self.verify_password(payload.password, user.password)
        if not is_valid:
            raise HTTPException(
                status_code=404,
                detail="Invalid credentials"
            )
        return user

def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)
