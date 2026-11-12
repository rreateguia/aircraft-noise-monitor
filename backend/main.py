
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Aircraft Noise Monitoring API",
    description="Simulated airport noise monitoring data",
    version="1.0.0"
)

# --------------------------------------------------
# 1. DATA
# --------------------------------------------------

stations = [
    {
        "id": 1,
        "name": "Station North",
        "latitude": 50.05,
        "longitude": 8.55
    },
    {
        "id": 2,
        "name": "Station South",
        "latitude": 49.98,
        "longitude": 8.62
    }
]

aircraft = [
    {
        "id": 1,
        "flight_number": "LH123",
        "airline": "Lufthansa",
        "aircraft_type": "A320",
        "registration": "D-AIAB",
        "origin": "FRA",
        "destination": "LIM"
    },
    {
        "id": 2,
        "flight_number": "BA456",
        "airline": "British Airways",
        "aircraft_type": "B787",
        "registration": "G-ZBKA",
        "origin": "LHR",
        "destination": "FRA"
    }
]

measurements = []
next_measurement_id = 1


# --------------------------------------------------
# 2. REQUEST MODEL
# --------------------------------------------------

class MeasurementCreate(BaseModel):
    station_id: int
    aircraft_id: int
    noise_level_db: float = Field(gt=0, le=200)
    timestamp: datetime


# --------------------------------------------------
# 3. HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {"message": "Aircraft Noise Monitoring API"}


# --------------------------------------------------
# 4. STATIONS
# --------------------------------------------------

@app.get("/api/stations")
def get_stations():
    return stations


@app.get("/api/stations/{station_id}")
def get_one_station(station_id: int):
    station = next(
        (s for s in stations if s["id"] == station_id),
        None
    )

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found"
        )

    return station


@app.delete("/api/stations/{station_id}")
def remove_station(station_id: int):
    station = next(
        (s for s in stations if s["id"] == station_id),
        None
    )

    if station is None:
        raise HTTPException(status_code=404, detail="Station not found")

    stations.remove(station)

    return {"message": "Station deleted", "station_id": station_id}


# --------------------------------------------------
# 5. AIRCRAFT
# --------------------------------------------------

@app.get("/api/aircraft")
def get_aircraft(
    flight_number: str | None = None,
    airline: str | None = None,
    aircraft_type: str | None = None
):
    result = aircraft

    if flight_number:
        result = [
            a for a in result
            if a["flight_number"].lower() == flight_number.lower()
        ]

    if airline:
        result = [
            a for a in result
            if a["airline"].lower() == airline.lower()
        ]

    if aircraft_type:
        result = [
            a for a in result
            if a["aircraft_type"].lower() == aircraft_type.lower()
        ]

    return result


@app.get("/api/aircraft/{aircraft_id}")
def get_one_aircraft(aircraft_id: int):
    item = next(
        (a for a in aircraft if a["id"] == aircraft_id),
        None
    )

    if item is None:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    return item


# --------------------------------------------------
# 6. MEASUREMENTS
# --------------------------------------------------

@app.get("/api/measurements")
def get_measurements(
    station_id: int | None = None,
    aircraft_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None
):
    result = measurements

    if station_id is not None:
        result = [
            m for m in result
            if m["station_id"] == station_id
        ]

    if aircraft_id is not None:
        result = [
            m for m in result
            if m["aircraft_id"] == aircraft_id
        ]

    if start_date is not None:
        result = [
            m for m in result
            if m["timestamp"] >= start_date
        ]

    if end_date is not None:
        result = [
            m for m in result
            if m["timestamp"] <= end_date
        ]

    return result


@app.post("/api/measurements", status_code=201)
def add_measurement(data: MeasurementCreate):
    global next_measurement_id

    # Validate station
    if not any(s["id"] == data.station_id for s in stations):
        raise HTTPException(status_code=404, detail="Station not found")

    # Validate aircraft
    if not any(a["id"] == data.aircraft_id for a in aircraft):
        raise HTTPException(status_code=404, detail="Aircraft not found")

    new_measurement = {
        "id": next_measurement_id,
        **data.model_dump()
    }

    measurements.append(new_measurement)
    next_measurement_id += 1

    return new_measurement
