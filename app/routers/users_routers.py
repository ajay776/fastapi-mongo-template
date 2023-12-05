from app.utils.users_utils import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_active_user, refresh_token, create_refresh_token, register_user
from fastapi.security import OAuth2PasswordRequestForm, HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, status
from app.schemas.users_schema import User, Token, UserRegistration
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter


router = APIRouter(
    prefix="", tags=["Authentication"]
)


@router.post("/register")
def register_user1(data: UserRegistration):
    response = register_user(data)
    return response


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(
        form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.get("username"), "email": user.get("email"), "is_active": user.get("is_active")}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"username": user.get("username"), "email": user.get("email"), "is_active": user.get("is_active")}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@router.post("/token/refresh", response_model=dict)
async def refresh_token_endpoint(token_data: dict = Depends(refresh_token)):
    return token_data
