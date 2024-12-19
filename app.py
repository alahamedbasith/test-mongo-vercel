from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Load MongoDB connection string from environment variable
MONGODB_URI = os.getenv("MONGODB_URI")
client = None

@app.on_event("startup")
async def startup_event():
    global client
    try:
        # Initialize MongoDB client
        client = AsyncIOMotorClient(MONGODB_URI)
        # Test connection by pinging the database
        await client.admin.command("ping")
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global client
    if client:
        client.close()

@app.get("/")
async def root():
    return {"message": "Connected successfully"} if client else {"message": "Not connected"}
