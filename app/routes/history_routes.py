from fastapi import APIRouter
from app.database import reports, prescriptions
from app.utils import serialize

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/{user_id}")
def get_history(user_id: str):

    user_reports = list(reports.find({"user_id": user_id}))
    user_pres = list(prescriptions.find({"user_id": user_id}))

    return {
        "reports": [serialize(r) for r in user_reports],
        "prescriptions": [serialize(p) for p in user_pres]
    }