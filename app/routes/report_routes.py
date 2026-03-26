from fastapi import APIRouter, UploadFile, File, Form
from datetime import datetime
from bson import ObjectId

from app.database import reports, fs
from app.services.preprocess_client import call_preprocess
from app.services.ocr_client import call_ocr
from app.services.ai_client import call_ai

router = APIRouter(prefix="/reports", tags=["Reports"])


# ============================
# HELPER (BEST PRACTICE)
# ============================

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])

    if "file_id" in doc:
        doc["file_id"] = str(doc["file_id"])

    if "created_at" in doc:
        doc["created_at"] = doc["created_at"].isoformat()

    if "updated_at" in doc:
        doc["updated_at"] = doc["updated_at"].isoformat()

    return doc


# ============================
# 1. UPLOAD REPORT
# ============================

@router.post("/upload")
async def upload_report(
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

    res = reports.insert_one(doc)
    doc["_id"] = str(res.inserted_id)

    # ✅ FIX: convert datetime before returning
    doc = serialize_doc(doc)

    return {"status": "uploaded", "data": doc}


# ============================
# 2. PROCESS REPORT
# ============================

@router.post("/process/{report_id}")
def process_report(report_id: str):

    doc = reports.find_one({"_id": ObjectId(report_id)})

    if not doc:
        return {"error": "Report not found"}

    file_bytes = fs.get(ObjectId(doc["file_id"])).read()

    processed_file = call_preprocess(file_bytes)
    ocr_result = call_ocr(processed_file)
    ai_result = call_ai(ocr_result["raw_text"])

    reports.update_one(
        {"_id": ObjectId(report_id)},
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
# 3. GET REPORT
# ============================

@router.get("/{report_id}")
def get_report(report_id: str):

    doc = reports.find_one({"_id": ObjectId(report_id)})

    if not doc:
        return {"error": "Not found"}

    # ✅ FIX: serialize before returning
    doc = serialize_doc(doc)

    return doc