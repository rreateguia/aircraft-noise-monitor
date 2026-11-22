
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from sqlmodel import Session, select

from database import engine, create_db_and_tables, get_session
from models import Station, Aircraft, Measurement


# --------------------------------------------------
# 1. DATABASE INITIALIZATION
# --------------------------------------------------

def initialize_database():
    create_db_and_tables()

    with Session(engine) as session:

        # Seed stations if table is empty
        if not session.exec(select(Station)).first():

            session.add_all([
                Station(
                    name="Station North",
                    latitude=50.05,
                    longitude=8.55
                ),
                Station(
                    name="Station South",
                    latitude=49.98,
                    longitude=8.62
                )
            ])

        # Seed aircraft if table is empty
        if not session.exec(select(Aircraft)).first():

            session.add_all([
                Aircraft(
                    flight_number="LH123",
                    airline="Lufthansa",
                    aircraft_type="A320",
                    registration="D-AIAB",
                    origin="FRA",
                    destination="PEK"
                ),
                Aircraft(
                    flight_number="BA456",
                    airline="British Airways",
                    aircraft_type="B787",
                    registration="G-ZBKA",
                    origin="LHR",
                    destination="FRA"
                )
            ])

        session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


# --------------------------------------------------
# 2. FASTAPI APPLICATION
# --------------------------------------------------

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
    ],
    lifespan=lifespan
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
# 3. REQUEST MODELS
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
# 4. HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {"message": "Aircraft Noise Monitoring API"}


# --------------------------------------------------
# 5. STATIONS
# --------------------------------------------------

@app.get(
    "/api/stations",
    tags=["Stations"],
    summary="Get all monitoring stations",
    description="Returns all registered airport noise monitoring stations."
)
def get_stations(session: Session = Depends(get_session)):

    statement = select(Station)

    return session.exec(statement).all()


@app.post(
    "/api/stations",
    tags=["Stations"],
    summary="Create a monitoring station",
    description="Register a new airport noise monitoring station.",
    status_code=201
)
def add_station(
    data: StationCreate,
    session: Session = Depends(get_session)
):

    new_station = Station(**data.model_dump())

    session.add(new_station)
    session.commit()
    session.refresh(new_station)

    return new_station


@app.get(
    "/api/stations/{station_id}",
    tags=["Stations"],
    summary="Get station by ID",
    description="Get one station using its ID."
)
def get_one_station(
    station_id: int,
    session: Session = Depends(get_session)
):

    station = session.get(Station, station_id)

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
    description="Delete one station using its ID."
)
def remove_station(
    station_id: int,
    session: Session = Depends(get_session)
):

    station = session.get(Station, station_id)

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found"
        )

    # Prevent deleting a station that has measurements
    statement = select(Measurement).where(
        Measurement.station_id == station_id
    )

    if session.exec(statement).first():
        raise HTTPException(
            status_code=409,
            detail="Cannot delete station with existing measurements"
        )

    session.delete(station)
    session.commit()

    return {
        "message": "Station deleted",
        "station_id": station_id
    }


# --------------------------------------------------
# 6. AIRCRAFT
# --------------------------------------------------

@app.get(
    "/api/aircraft",
    tags=["Aircraft"],
    summary="Get aircraft information",
    description="Returns aircraft information with optional filters."
)
def get_aircraft(
    flight_number: str | None = None,
    airline: str | None = None,
    aircraft_type: str | None = None,
    session: Session = Depends(get_session)
):

    statement = select(Aircraft)

    if flight_number:
        statement = statement.where(
            Aircraft.flight_number.ilike(flight_number)
        )

    if airline:
        statement = statement.where(
            Aircraft.airline.ilike(airline)
        )

    if aircraft_type:
        statement = statement.where(
            Aircraft.aircraft_type.ilike(aircraft_type)
        )

    return session.exec(statement).all()


@app.post(
    "/api/aircraft",
    tags=["Aircraft"],
    summary="Register a new aircraft",
    description="Register aircraft information.",
    status_code=201
)
def add_aircraft(
    data: AircraftCreate,
    session: Session = Depends(get_session)
):

    new_aircraft = Aircraft(**data.model_dump())

    session.add(new_aircraft)
    session.commit()
    session.refresh(new_aircraft)

    return new_aircraft


@app.get(
    "/api/aircraft/{aircraft_id}",
    tags=["Aircraft"],
    summary="Get aircraft by ID",
    description="Get aircraft using its ID."
)
def get_one_aircraft(
    aircraft_id: int,
    session: Session = Depends(get_session)
):

    item = session.get(Aircraft, aircraft_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Aircraft not found"
        )

    return item


# --------------------------------------------------
# 7. MEASUREMENTS
# --------------------------------------------------

@app.get(
    "/api/measurements",
    tags=["Measurements"],
    summary="Get and filter measurements",
    description="Get measurements using optional filters."
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
    ),
    session: Session = Depends(get_session)
):

    statement = select(Measurement)

    # Validate station
    if station_id is not None:

        if session.get(Station, station_id) is None:
            raise HTTPException(
                status_code=404,
                detail="Station not found"
            )

        statement = statement.where(
            Measurement.station_id == station_id
        )

    # Validate aircraft
    if aircraft_id is not None:

        if session.get(Aircraft, aircraft_id) is None:
            raise HTTPException(
                status_code=404,
                detail="Aircraft not found"
            )

        statement = statement.where(
            Measurement.aircraft_id == aircraft_id
        )

    # Apply date filters
    if start_date is not None:
        statement = statement.where(
            Measurement.timestamp >= start_date
        )

    if end_date is not None:
        statement = statement.where(
            Measurement.timestamp <= end_date
        )

    # Apply noise level filter
    if min_noise_level is not None:
        statement = statement.where(
            Measurement.noise_level_db >= min_noise_level
        )

    return session.exec(statement).all()


@app.post(
    "/api/measurements",
    tags=["Measurements"],
    summary="Create a noise measurement",
    description="Create a new aircraft noise measurement.",
    status_code=201
)
def add_measurement(
    data: MeasurementCreate,
    session: Session = Depends(get_session)
):

    # Validate station
    if session.get(Station, data.station_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found"
        )

    # Validate aircraft
    if session.get(Aircraft, data.aircraft_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Aircraft not found"
        )

    new_measurement = Measurement(**data.model_dump())

    session.add(new_measurement)
    session.commit()
    session.refresh(new_measurement)

    return new_measurement
