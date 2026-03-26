from fastapi import APIRouter, UploadFile, File, Form
from datetime import datetime
from bson import ObjectId

from app.database import prescriptions, fs
from app.services.preprocess_client import call_preprocess
from app.services.ocr_client import call_ocr
from app.services.ai_client import call_ai

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


# ============================
# 1. UPLOAD PRESCRIPTION
# ============================

@router.post("/upload")
async def upload_prescription(
    user_id: str = Form(...),
    file: UploadFile = File(...)
):
    file_id = fs.put(await file.read(), filename=file.filename)

    doc = {
        "user_id": user_id,
        "file_id": str(file_id),

        "status": "uploaded",
        "raw_text": None,
        "ai_data": None,

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    res = prescriptions.insert_one(doc)

    # ✅ Convert before returning
    doc["_id"] = str(res.inserted_id)
    doc["created_at"] = doc["created_at"].isoformat()
    doc["updated_at"] = doc["updated_at"].isoformat()

    return {"status": "uploaded", "data": doc}


# ============================
# 2. PROCESS PRESCRIPTION
# ============================

@router.post("/process/{prescription_id}")
def process_prescription(prescription_id: str):

    doc = prescriptions.find_one({"_id": ObjectId(prescription_id)})

    if not doc:
        return {"error": "Prescription not found"}

    file_bytes = fs.get(ObjectId(doc["file_id"])).read()

    processed_file = call_preprocess(file_bytes)
    ocr_result = call_ocr(processed_file)
    ai_result = call_ai(ocr_result["raw_text"])

    prescriptions.update_one(
        {"_id": ObjectId(prescription_id)},
        {"$set": {
            "raw_text": ocr_result["raw_text"],
            "ai_data": ai_result,
            "status": "completed",
            "updated_at": datetime.utcnow()
        }}
    )

    return {
        "status": "completed",
        "ai_data": ai_result
    }


# ============================
# 3. GET PRESCRIPTION
# ============================

@router.get("/{prescription_id}")
def get_prescription(prescription_id: str):

    doc = prescriptions.find_one({"_id": ObjectId(prescription_id)})

    if not doc:
        return {"error": "Not found"}

    # ✅ Convert ALL non-serializable fields
    doc["_id"] = str(doc["_id"])
    doc["file_id"] = str(doc["file_id"])

    if "created_at" in doc:
        doc["created_at"] = doc["created_at"].isoformat()

    if "updated_at" in doc:
        doc["updated_at"] = doc["updated_at"].isoformat()

    return doc