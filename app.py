from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import motor.motor_asyncio  # Use motor for async MongoDB operations
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

# Load MongoDB connection string from environment variable
MONGODB_URI = os.getenv("MONGODB_URI")

# MongoDB setup
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Could not connect to MongoDB: {e}")

db = client.portfolio
collection = db.content

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Content(BaseModel):
    html_content: str

@app.post("/update_content/")
async def update_content(html_content: str = Form(...)):
    # Save content to MongoDB
    try:
        await collection.update_one(
            {"_id": "content"},
            {"$set": {"html_content": html_content}},
            upsert=True
        )
        return {"message": "Content updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating content: {e}")

@app.get("/portfolio", response_class=HTMLResponse)
async def portfolio():
    document = await collection.find_one({"_id": "content"})
    if document:
        html_content = document["html_content"]
        return HTMLResponse(content=html_content)
    raise HTTPException(status_code=404, detail="Content not found")
