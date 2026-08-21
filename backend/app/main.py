from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.app.database import Base, engine, get_db
from backend.app.models import ClimateReading
from backend.app.schemas import Reading, ReadingCreate


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Tempest API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/readings", response_model=Reading, status_code=201)
def create_reading(
    payload: ReadingCreate,
    db: Annotated[Session, Depends(get_db)],
) -> ClimateReading:
    reading = ClimateReading(**payload.model_dump())
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@app.get("/readings", response_model=list[Reading])
def list_readings(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ClimateReading]:
    statement = (
        select(ClimateReading)
        .order_by(desc(ClimateReading.recorded_at), desc(ClimateReading.id))
        .limit(limit)
    )
    return list(db.scalars(statement))


@app.get("/readings/latest", response_model=Reading)
def latest_reading(db: Annotated[Session, Depends(get_db)]) -> ClimateReading:
    statement = (
        select(ClimateReading)
        .order_by(desc(ClimateReading.recorded_at), desc(ClimateReading.id))
        .limit(1)
    )
    reading = db.scalar(statement)

    if reading is None:
        raise HTTPException(status_code=404, detail="No readings have been recorded yet.")

    return reading
