from fastapi import APIRouter
from fastapi import Body
import os
import json
import motor.motor_asyncio
from bson import ObjectId

router = APIRouter(tags=["mongoDB"], prefix="/mongodb")

if "MONGO_CONNECTION_STRING" in os.environ:
    MONGO_CONNECTION_STRING = os.environ.get("MONGO_CONNECTION_STRING")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME")
    MONGO_COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_NAME")
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_CONNECTION_STRING)
    db = client[MONGO_DB_NAME]
    collection = db.get_collection(MONGO_COLLECTION_NAME)


# Example,
# {"categoryId": "some_category_id",
# "name": "Yamba Surfboard-51",
# "quantity": 1,
# "sale": false}
@router.post("")
async def mongo_add(product: dict = Body(...)):
    """Add a product to the database"""
    if "_id" in product.keys():
        result = await collection.update_one(
            {"_id": product["_id"]}, {"$set": product}, upsert=True
        )
    else:
        result = await collection.insert_one(product)
    res = await collection.find(product).to_list(1000)
    res = json.loads(json.dumps(res, default=str))
    return res


@router.get("")
async def mongo_dump():
    """Dump all documents in the collection"""
    # ObjectId causes issues. Convert to str first
    res = await collection.find().to_list(1000)
    res = json.loads(json.dumps(res, default=str))
    return res


# Example
# query = {"categoryId": "some_category_id"}
@router.post("/query")
async def mongo_query(query: dict = Body(...)):
    """Query for documents in the collection"""
    res = await collection.find(query).to_list(1000)
    res = json.loads(json.dumps(res, default=str))
    return res

@router.put("/{item_id}")
async def mongo_update(item_id: str, update_data: dict = Body(...)):
    """Update a product by its ID"""
    result = await collection.update_one(
        {"_id": ObjectId(item_id)}, {"$set": update_data}
    )
    if result.modified_count:
        updated = await collection.find_one({"_id": ObjectId(item_id)})
        return json.loads(json.dumps(updated, default=str))
    return {"message": "No document updated"}


@router.delete("/{item_id}")
async def mongo_delete(item_id: str):
    """Delete a product by its ID"""
    result = await collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count:
        return {"message": f"Product {item_id} deleted"}
    return {"message": "No document found to delete"}

