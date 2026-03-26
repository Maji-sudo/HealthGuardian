from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
from pymongo import MongoClient
from gridfs import GridFS
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URI)
db = client["health_guard"]

# ============================
# COLLECTIONS
# ============================

users = db["users"]
reports = db["reports"]
prescriptions = db["prescriptions"]

# ============================
# GRIDFS (IMPORTANT 🔥)
# ============================

fs = GridFS(db)