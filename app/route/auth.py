from fastapi import APIRouter, Depends
from ..schema.user_schema import UserCreate, UserWrapper, UserLogin
from ..service.auth import UserService, get_user_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserWrapper)
async def register_user(payload: UserCreate, user_service: UserService = Depends(get_user_service)):
    result = await user_service.create_user(payload)
    access_token = await user_service.create_token({"id": result.id, "email": result.email})
    return {
        "message": "user created successfully",
        "token": access_token,
        "user": result
    }

@router.post("/login", response_model=UserWrapper)
async def login(payload: UserLogin, user_service: UserService = Depends(get_user_service)):
    user = await user_service.login_user(payload)
    access_token = await user_service.create_token({"id": user.id, "email": user.email})
    return {
        "message": "user logged in successfully",
        "token": access_token,
        "user": user
    }