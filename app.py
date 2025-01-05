from fastapi import FastAPI, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import motor.motor_asyncio  # MongoDB
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI")
client = None
db = None
collection = None

@app.on_event("startup")
async def startup_db_client():
    global client, db, collection
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
    db = client.portfolio
    collection = db.content
    # MongoDB connection test
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(f"Could not connect to MongoDB: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

class Content(BaseModel):
    html_content: str

@app.get("/")
async def root():
    try:
        client.admin.command('ping')
        return {"message": "Successfully connected to MongoDB!"}
    except Exception as e:
        return {"message": f"Could not connect to MongoDB: {e}"}

# Background task to save content to DB
async def save_content_to_db(html_content):
    try:
        await collection.update_one(
            {"_id": "content"},
            {"$set": {"html_content": html_content}},
            upsert=True
        )
    except Exception as e:
        print(f"Error saving content to DB: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving content: {e}")

@app.post("/update_content/")
async def update_content(html_content: str, background_tasks: BackgroundTasks):
    try:
        # Use async task to save content to DB
        background_tasks.add_task(save_content_to_db, html_content)
        return {"message": "Content update is in progress."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating content: {e}")

@app.get("/portfolio", response_class=HTMLResponse)
async def portfolio():
    document = await collection.find_one({"_id": "content"})
    if document:
        html_content = document["html_content"]
        return HTMLResponse(content=html_content)
    raise HTTPException(status_code=404, detail="Content not found")
