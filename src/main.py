from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.business_profiles import router as business_profiles_router
from src.api.claims import router as claims_router
from src.api.comparisons import router as comparisons_router
from src.api.document_submissions import (
    router as document_submissions_router,
)
from src.api.policy_changes import router as policy_changes_router
from src.db.dependencies import get_db


app = FastAPI(
    title="Trusted Information Intelligence",
    version="0.1.0",
)


app.include_router(business_profiles_router)
app.include_router(claims_router)
app.include_router(policy_changes_router)
app.include_router(comparisons_router)
app.include_router(document_submissions_router)


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
