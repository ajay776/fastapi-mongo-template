from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.schemas.users_schema import UserInDB, TokenData, User
from app.schemas.common_schema import CommonResponseSchema
from datetime import datetime, timedelta
from app.exceptions import credentials_exception
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv
from typing import Annotated
from app.database import db
import os


user_collection = db["users"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    print("------------------------------", pwd_context.hash(password))
    return pwd_context.hash(password)


# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)


def register_user(user_data):
    import pdb
    pdb.set_trace()
    user = user_data.dict()
    hashed_password = get_password_hash(user.get("password"))
    user["password"] = hashed_password
    user = user_collection.insert_one(user)
    return CommonResponseSchema(type="success", status_code=201, message="user created sucessfully", data=user.acknowledged)


def authenticate_user(username: str, password: str):
    import pdb
    # pdb.set_trace()
    user = user_collection.find_one({"username": username})
    # user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.get("password")):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    # user = get_user(fake_users_db, username=token_data.username)
    user = user_collection.find_one(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def refresh_token(
    refresh_token: str = Depends(oauth2_scheme)
):

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": payload["sub"]}, expires_delta=access_token_expires)

    return {"access_token": new_access_token, "token_type": "bearer"}