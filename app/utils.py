from bson import ObjectId
from datetime import datetime

def serialize(doc):
    # Convert MongoDB ObjectId
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])

    # Convert file_id if exists
    if "file_id" in doc and isinstance(doc["file_id"], ObjectId):
        doc["file_id"] = str(doc["file_id"])

    # Convert datetime fields
    if "created_at" in doc and isinstance(doc["created_at"], datetime):
        doc["created_at"] = doc["created_at"].isoformat()

    if "updated_at" in doc and isinstance(doc["updated_at"], datetime):
        doc["updated_at"] = doc["updated_at"].isoformat()

    return doc