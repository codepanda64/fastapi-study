from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, Field


class NetworkBase(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None


class NetworkIn(NetworkBase):
    code: str = Field(
        min_length=2,
        max_length=5,
        description="Network code must be between 2 and 5 characters long",
        title="Network code",
    )
    name: str


class NetworkUpdate(NetworkIn):
    pass


class NetworkOut(NetworkBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PositionIn(BaseModel):
    latitude: float
    longitude: float
    elevation: float | None = None
    depth: float | None = None
    is_current: bool = True
    change_time: datetime


class PositionOut(BaseModel):
    id: int
    latitude: float
    longitude: float
    elevation: float | None = None
    depth: float | None = None
    is_current: bool
    change_time: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StationIn(BaseModel):
    network_id: int
    code: str = Field(
        min_length=3,
        max_length=6,
        description="Station code must be between 3 and 6 characters long",
        title="Station code",
    )
    name: str
    address: str | None = ""
    position: PositionIn | None = None


# Station 简化输出模型（不包含 network）
class StationSimpleOut(BaseModel):
    id: int
    network_id: int
    code: str
    name: str
    address: str | None = ""
    current_position: Optional[PositionOut] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Station 完整输出模型（包含 network）
class StationOut(StationSimpleOut):
    network: NetworkOut
