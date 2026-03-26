from fastapi import APIRouter
from datetime import datetime
from app.database import users
from app.schemas import UserCreate

router = APIRouter(prefix="/users", tags=["Users"])


# ============================
# HELPER
# ============================

def serialize_user(doc):
    doc["_id"] = str(doc["_id"])

    if "created_at" in doc:
        doc["created_at"] = doc["created_at"].isoformat()

    return doc


# ============================
# REGISTER USER
# ============================

@router.post("/register")
def register(user: UserCreate):

    # ✅ Check if email already exists
    if users.find_one({"email": user.email}):
        return {"error": "Email already exists"}

    user_data = {
        "name": user.name,
        "email": user.email,
        "password": user.password,   # ⚠️ plain text (basic version)
        "created_at": datetime.utcnow()
    }

    res = users.insert_one(user_data)
    user_data["_id"] = res.inserted_id

    user_data = serialize_user(user_data)

    return {
        "status": "created",
        "data": user_data
    }


# ============================
# LOGIN USER (Basic)
# ============================

@router.post("/login")
def login(user: UserCreate):

    existing_user = users.find_one({"email": user.email})

    if not existing_user:
        return {"error": "User not found"}

    # ❌ plain password check
    if existing_user["password"] != user.password:
        return {"error": "Invalid password"}

    existing_user = serialize_user(existing_user)

    return {
        "status": "login successful",
        "data": existing_user
    }