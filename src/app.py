"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from contextlib import asynccontextmanager
import motor.motor_asyncio
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

# MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
db = client.mergington_high
activities_collection = db.activities

# Initial activities data
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball games",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "isabella@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn and practice tennis with peers",
        "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 10,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Swimming Team": {
        "description": "Train and compete in swimming competitions",
        "schedule": "Tuesdays and Fridays, 3:00 PM - 4:30 PM",
        "max_participants": 12,
        "participants": ["elijah@mergington.edu", "amelia@mergington.edu"]
    },
    "Drama Club": {
        "description": "Explore acting and participate in school plays",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["charlotte@mergington.edu", "harper@mergington.edu"]
    },
    "Art Workshop": {
        "description": "Learn painting, sketching, and other art techniques",
        "schedule": "Fridays, 3:00 PM - 4:30 PM",
        "max_participants": 15,
        "participants": ["ella@mergington.edu", "grace@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging math problems and prepare for competitions",
        "schedule": "Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 25,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Mondays, 3:30 PM - 4:30 PM",
        "max_participants": 18,
        "participants": ["henry@mergington.edu", "alexander@mergington.edu"]
    },
    "69 Workshop": {
        "description": "A workshop for students interested in have the greatest time of their lives",
        "schedule": "Fridays, 8:00 PM - 9:00 PM",
        "max_participants": 8,
        "participants": []
    }
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    await activities_collection.delete_many({})
    for name, details in initial_activities.items():
        await activities_collection.insert_one({"name": name, **details})
    yield

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities",
              lifespan=lifespan)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")

@app.get("/activities")
async def get_activities() -> Dict[str, Any]:
    """Get all activities with their details."""
    cursor = activities_collection.find({}, {'_id': 0})
    activities_list = await cursor.to_list(length=100)
    
    # Convert to the expected format with activity name as key
    return {activity.pop('name'): activity for activity in activities_list}

@app.post("/activities/{activity_name}/signup")
async def signup_activity(activity_name: str, email: str):
    """Sign up for an activity."""
    # Get the activity
    activity = await activities_collection.find_one({"name": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Already signed up for this activity")

    # Check if activity is full
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add participant
    await activities_collection.update_one(
        {"name": activity_name},
        {"$push": {"participants": email}}
    )
    
    return {"message": f"Successfully signed up for {activity_name}"}

@app.post("/activities/{activity_name}/unregister")
async def unregister_activity(activity_name: str, email: str):
    """Unregister from an activity."""
    # Get the activity
    activity = await activities_collection.find_one({"name": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if actually signed up
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Not registered for this activity")

    # Remove participant
    await activities_collection.update_one(
        {"name": activity_name},
        {"$pull": {"participants": email}}
    )
    
    return {"message": f"Successfully unregistered from {activity_name}"}
