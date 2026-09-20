from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.claims import router as claims_router
from src.db.dependencies import get_db


app = FastAPI(
    title="Trusted Information Intelligence",
    version="0.1.0",
)


app.include_router(claims_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def database_health_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": result.scalar(),
    }
