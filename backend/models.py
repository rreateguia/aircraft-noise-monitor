
from datetime import datetime

from sqlmodel import SQLModel, Field


# --------------------------------------------------
# STATIONS TABLE
# --------------------------------------------------

class Station(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str
    latitude: float
    longitude: float


# --------------------------------------------------
# AIRCRAFT TABLE
# --------------------------------------------------

class Aircraft(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    flight_number: str
    airline: str
    aircraft_type: str
    registration: str
    origin: str
    destination: str


# --------------------------------------------------
# MEASUREMENTS TABLE
# --------------------------------------------------

class Measurement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    station_id: int = Field(foreign_key="station.id")
    aircraft_id: int = Field(foreign_key="aircraft.id")

    noise_level_db: float
    timestamp: datetime
