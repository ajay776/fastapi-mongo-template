import os
from fastapi import FastAPI
from app.routers import users_routers
from app.database import db_url
app = FastAPI()
app.include_router(users_routers.router)
