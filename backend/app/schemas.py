from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


class WaypointCreate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    order: int = Field(..., ge=1)


class RouteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    waypoints: List[WaypointCreate]

    @field_validator("waypoints")
    @classmethod
    def ensure_non_empty(cls, value: List[WaypointCreate]):
        if not value:
            raise ValueError("Se requiere al menos un waypoint")
        return value


class WaypointOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    latitude: float
    longitude: float
    order: int = Field(serialization_alias="order")


class RouteBasicOut(BaseModel):
    id: int
    name: str
    waypoint_count: int
    total_distance_meters: float
    created_at: datetime


class RouteDetailOut(BaseModel):
    id: int
    name: str
    waypoints: List[WaypointOut]
    total_distance_meters: float
    created_at: datetime
