from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os

db_url = os.getenv("DB_URL")

client = MongoClient(db_url)

db = client["fastapi_mongo_boiler"]
