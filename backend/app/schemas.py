from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ReadingCreate(BaseModel):
    temp_c: Annotated[float, Field(ge=-40, le=80)]
    humidity: Annotated[float, Field(ge=0, le=100)]
    source: str = "arduino-uno-dht11"


class Reading(ReadingCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recorded_at: datetime
