from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# MongoDB setup
import motor.motor_asyncio  # Use motor for async MongoDB operations
import os
from dotenv import load_dotenv, dotenv_values

# Load environment variables from .env file
load_dotenv()

# Access environment variables directly using dotenv_values() without os
env = dotenv_values()  # This loads the .env file into a dictionary

# MongoDB URI directly from the dotenv dictionary
MONGODB_URI = env.get("MONGODB_URI")

# MongoDB setup
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Could not connect to MongoDB: {e}")

# Create a new client and connect to the server using motor
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client.portfolio
collection = db.content

app = FastAPI()

class Content(BaseModel):
    html_content: str

@app.get("/", response_class=HTMLResponse)
async def read_form():
    return """
    <html>
        <body>
            <h2>Admin Panel</h2>
            <form action="/update_content/" method="post">
                <textarea name="html_content" rows="10" cols="50">Enter HTML content here...</textarea><br>
                <input type="submit" value="Update Content">
            </form>
        </body>
    </html>
    """

@app.post("/update_content/")
async def update_content(html_content: str = Form(...)):
    # Save content to MongoDB
    await collection.update_one(
        {"_id": "content"},
        {"$set": {"html_content": html_content}},
        upsert=True
    )
    return {"message": "Content updated successfully"}

@app.get("/portfolio", response_class=HTMLResponse)
async def portfolio():
    document = await collection.find_one({"_id": "content"})
    if document:
        html_content = document["html_content"]
        return f"""
        <html>
            <body>
                <h1>Welcome to My Portfolio</h1>
                <div>{html_content}</div>
                
            </body>
        </html>
        """
    return "<html><body><h1>No content available</h1></body></html>"
