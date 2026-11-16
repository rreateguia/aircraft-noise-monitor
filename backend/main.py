
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Aircraft Noise Monitoring API",
    description="""
    REST API for a simulated airport noise monitoring system.

    The API provides:
    - Airport noise monitoring stations
    - Aircraft information
    - Noise measurements
    - Filtering by station, aircraft, date and noise level

    This project uses simulated data for educational purposes.
    """,
    version="1.0.0",
    contact={
        "name": "Rolando Reategui",
        "url": "https://github.com/rreateguia"
    },
    openapi_tags=[
        {
            "name": "Stations",
            "description": "Operations for airport noise monitoring stations."
        },
        {
            "name": "Aircraft",
            "description": "Operations for aircraft information."
        },
        {
            "name": "Measurements",
            "description": "Create and retrieve aircraft noise measurements."
        }
    ]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        "destination": "PEK"
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


class StationCreate(BaseModel):
    name: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class AircraftCreate(BaseModel):
    flight_number: str
    airline: str
    aircraft_type: str
    registration: str
    origin: str
    destination: str


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

@app.get(
    "/api/stations",
    tags=["Stations"],
    summary="Get all monitoring stations",
    description="Returns all registered airport noise monitoring stations."
    )
def get_stations():
    return stations

@app.post(
    "/api/stations",
    tags=["Stations"],
    summary="Create a monitoring station",
    description="Register a new airport noise monitoring station.",
    status_code=201
)
def add_station(data: StationCreate):
    new_station = {
        "id": max((s["id"] for s in stations), default=0) + 1,
        **data.model_dump()
    }

    stations.append(new_station)

    return new_station
@app.get(
    "/api/stations/{station_id}",
    tags=["Stations"],
    summary="Get station by ID",
    description="Get one station using its ID"
    )
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


@app.delete(
    "/api/stations/{station_id}",
    tags=["Stations"],
    summary="Delete a monitoring station",
    description="Delete one station using its ID"
    )
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

@app.get(
    "/api/aircraft",
    tags=["Aircraft"],
    summary="Get aircraft information",
    description="Returns all aircraft using its parameters"
        )
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

@app.post(
    "/api/aircraft",
    tags=["Aircraft"],
    summary="Register a new aircraft",
    description="Register aircraft information.",
    status_code=201
)
def add_aircraft(data: AircraftCreate):
    new_aircraft = {
        "id": max((a["id"] for a in aircraft), default=0) + 1,
        **data.model_dump()
    }

    aircraft.append(new_aircraft)

    return new_aircraft

@app.get(
        "/api/aircraft/{aircraft_id}",
        tags=["Aircraft"],
        summary="Get aircraft by ID",
        description="Get aircraft using its ID"
        )
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

@app.get(
        "/api/measurements",
        tags=["Measurements"],
        summary="Get and filter measurements",
        description="Get a measurement using its parameters"   
        )
def get_measurements(
    station_id: int | None = Query(
        default=None,
        description="Filter by monitoring station ID."
    ),
    aircraft_id: int | None = Query(
        default=None,
        description="Filter by aircraft ID."
    ),
    start_date: datetime | None = Query(
        default=None,
        description="Return measurements from this timestamp onwards."
    ),
    end_date: datetime | None = Query(
        default=None,
        description="Return measurements up to this timestamp."
    ),
    min_noise_level: float | None = Query(
        default=None,
        description="Minimum noise level in decibels (dB)."
    )
):
    print("Received min_noise_level:", min_noise_level)
    print("Stored measurements:", measurements)
    result = measurements

    if station_id is not None:
        if not any(s["id"] == station_id for s in stations):
            raise HTTPException(
                status_code=404,
                detail="Station not found"
            )
    if station_id is not None:
        result = [
            m for m in result
            if m["station_id"] == station_id
        ]
    
    if aircraft_id is not None:
        if not any(a["id"] == aircraft_id for a in aircraft):
            raise HTTPException(
                status_code=404,
                detail="Aircraft not found"
            )
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
    if min_noise_level is not None:
        result = [
            m for m in result
            if m["noise_level_db"] >= min_noise_level
        ]
    print("Filtered results:", result)
    return result


@app.post(
        "/api/measurements", 
        tags=["Measurements"],
        summary="Create a noise measurement",
        description="Create a measurement using an object from class MeasurementCreate",
        status_code=201
        )
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
