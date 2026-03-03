from pydantic import BaseModel
from datetime import datetime


class Bin(BaseModel):
    bin_id: str
    city: str
    latitude: float
    longitude: float
    fill_level: float
    fill_rate: float
    last_updated: datetime


class BinUpdatePayload(BaseModel):
    bin_id: str
    city: str
    latitude: float
    longitude: float
    fill_level: float
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    bins: int
    simulation_active: bool


class MessageResponse(BaseModel):
    message: str
