from fastapi import FastAPI
from app.routes import report_routes, prescription_routes, users_routes, history_routes

app = FastAPI()

app.include_router(users_routes.router)
app.include_router(report_routes.router)
app.include_router(prescription_routes.router)
app.include_router(history_routes.router)


@app.get("/")
def home():
    return {"message": "Health Guard API Running"}