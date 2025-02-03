from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, Field


class HistoryBase(BaseModel):
    created_at: datetime


class StationPositionHistoryOut(HistoryBase):
    id: int
    latitude: float
    longitude: float
    elevation: float | None = None
    depth: float | None = None
    changed_at: datetime
    is_virtual: bool
    is_current: bool

    model_config = ConfigDict(from_attributes=True)
