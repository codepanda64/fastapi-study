from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, validator


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


def validate_geo_range(
    value: float, name: str, min_value: float, max_value: float
) -> float:
    if not min_value <= value <= max_value:
        raise ValueError(f"{name} must be between {min_value} and {max_value}")
    return value


class PositionBase(BaseModel):
    latitude: float = -999
    longitude: float = -999
    elevation: Optional[float] = None
    depth: Optional[float] = None
    changed_at: datetime


class PositionIn(PositionBase):
    elevation: Optional[float] = Field(default=None, nullable=True)
    depth: Optional[float] = Field(default=None, nullable=True)
    model_config = ConfigDict(from_attributes=True)

    @field_validator("latitude")
    def latitude_range(cls, value):
        return validate_geo_range(value, "Latitude", -90, 90)

    @field_validator("longitude")
    def longitude_range(cls, value):
        return validate_geo_range(value, "Longitude", -180, 180)


class PositionOut(PositionBase):
    id: int
    is_virtual: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StationSimpleIn(BaseModel):
    network_id: int
    code: str = Field(
        min_length=3,
        max_length=6,
        description="Station code must be between 3 and 6 characters long",
        title="Station code",
    )
    name: Optional[str] = None
    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StationIn(StationSimpleIn):
    position: Optional[PositionIn] = None


# Station 简化输出模型（不包含 network）
class StationSimpleOut(BaseModel):
    id: int
    network_id: int
    code: str
    name: str

    model_config = ConfigDict(from_attributes=True)


# Station 完整输出模型（包含 network）
class StationOut(StationSimpleOut):
    network: NetworkOut
    address: Optional[str] = None
    position: Optional[PositionOut] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
