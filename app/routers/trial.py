from fastapi import APIRouter, Body, HTTPException
from bson import ObjectId
import json
import os
import motor.motor_asyncio
from bson.errors import InvalidId

router = APIRouter(tags=["trialTable"], prefix="/trialtable")
from ..models.trials import TrialCreate, TrialUpdate


MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_CONNECTION_STRING)
MONGO_COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_NAME_FOR_TRIALS")
db = client[MONGO_DB_NAME]
collection = db.get_collection(MONGO_COLLECTION_NAME)


@router.post("/")
async def create_trial(trial: TrialCreate):
    """Create a Trial"""
    trial_dict = trial.dict()
    result = await collection.insert_one(trial_dict)
    trial_dict["_id"] = str(result.inserted_id)
    return trial_dict


@router.get("/")
async def list_trials():
    """List Trials"""
    trials = await collection.find().to_list(1000)
    return json.loads(json.dumps(trials, default=str))


@router.get("/{trial_id}")
async def get_trial(trial_id: str):
    """Get one Trial based on ID"""
    trial = await collection.find_one({"_id": ObjectId(trial_id)})
    if trial:
        return json.loads(json.dumps(trial, default=str))
    raise HTTPException(status_code=404, detail="Trial not found")


@router.put("/{trial_id}")
async def update_trial(trial_id: str, trial_update: TrialUpdate = Body(...)):
    """Update all or some fields of a Trial based on ID"""
    try:
        object_id = ObjectId(trial_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid trial ID format")

    update_data = trial_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Missing update data")

    try:
        result = await collection.update_one({"_id": object_id}, {"$set": update_data})
        if result.modified_count:
            updated = await collection.find_one({"_id": object_id})
            return json.loads(json.dumps(updated, default=str))
        return {"message": "No document updated"}
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{trial_id}")
async def delete_trial(trial_id: str):
    result = await collection.delete_one({"_id": ObjectId(trial_id)})
    if result.deleted_count:
        return {"message": f"Trial {trial_id} deleted"}
    return {"message": "No document found to delete"}
