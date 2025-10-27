# app/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os

# --- MongoDB Atlas Connection ---
MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb+srv://premmkuruva_db_user:p%40ssw0rd%279%27%21@cluster0.pm96bwr.mongodb.net/?retryWrites=true&w=majority"
)

client = AsyncIOMotorClient(MONGO_URL, server_api=ServerApi('1'))
db = client["todo_db"]  # database name
todo_collection = db["todos"]

# --- Optional ping to check connection ---
async def init_db():
    try:
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)
