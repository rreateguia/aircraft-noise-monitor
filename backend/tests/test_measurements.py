

from datetime import datetime, timezone

import pytest
import main

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from database import get_session
from models import Station, Aircraft, Measurement

def test_home(client_with_measurements):
    response = client_with_measurements.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Aircraft Noise Monitoring API"
    }


def test_get_stations(client_with_measurements):
    response = client_with_measurements.get("/api/stations")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
@pytest.fixture
def client_with_measurements():
    # Create an isolated in-memory SQLite database
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(test_engine)

    # Insert test stations, aircraft, and measurements
    with Session(test_engine) as session:
        session.add_all([
            Station(
                id=1,
                name="Test Station North",
                latitude=50.05,
                longitude=8.55,
            ),
            Station(
                id=2,
                name="Test Station South",
                latitude=49.98,
                longitude=8.62,
            ),
            Aircraft(
                id=1,
                flight_number="LH123",
                airline="Lufthansa",
                aircraft_type="A320",
                registration="D-AIAB",
                origin="FRA",
                destination="PEK",
            ),
            Aircraft(
                id=2,
                flight_number="BA456",
                airline="British Airways",
                aircraft_type="B787",
                registration="G-ZBKA",
                origin="LHR",
                destination="FRA",
            ),
        ])

        session.add_all([
            Measurement(
                id=1,
                station_id=1,
                aircraft_id=1,
                noise_level_db=52.45,
                timestamp=datetime(2026, 11, 10, 8, 15, tzinfo=timezone.utc),
            ),
            Measurement(
                id=2,
                station_id=1,
                aircraft_id=2,
                noise_level_db=74.80,
                timestamp=datetime(2026, 11, 11, 9, 45, tzinfo=timezone.utc),
            ),
            Measurement(
                id=3,
                station_id=2,
                aircraft_id=1,
                noise_level_db=88.40,
                timestamp=datetime(2026, 11, 12, 18, 45, tzinfo=timezone.utc),
            ),
            Measurement(
                id=4,
                station_id=2,
                aircraft_id=2,
                noise_level_db=63.90,
                timestamp=datetime(2026, 11, 13, 6, 50, tzinfo=timezone.utc),
            ),
        ])

        session.commit()

    # Override the application's database dependency
    def get_test_session():
        with Session(test_engine) as session:
            yield session

    main.app.dependency_overrides[get_session] = get_test_session

    # Do not use the TestClient context manager here:
    # that would trigger the application's production database lifespan.
    test_client = TestClient(main.app)

    yield test_client

    # Clean up after each test
    test_client.close()
    main.app.dependency_overrides.clear()
    test_engine.dispose()

def test_get_all_measurements(client_with_measurements):
    response = client_with_measurements.get("/api/measurements")

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_filter_by_station(client_with_measurements):
    response = client_with_measurements.get(
        "/api/measurements?station_id=1"
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 2
    assert all(m["station_id"] == 1 for m in results)


def test_filter_by_aircraft(client_with_measurements):
    response = client_with_measurements.get(
        "/api/measurements?aircraft_id=1"
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 2
    assert all(m["aircraft_id"] == 1 for m in results)


def test_filter_by_min_noise_level(client_with_measurements):
    response = client_with_measurements.get(
        "/api/measurements?min_noise_level=70"
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 2
    assert all(m["noise_level_db"] >= 70 for m in results)
def test_min_noise_level_no_results(client_with_measurements):
    response = client_with_measurements.get(
        "/api/measurements?min_noise_level=150"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_invalid_station_id(client_with_measurements):
    response = client_with_measurements.get(
        "/api/measurements?station_id=999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Station not found"


valid_measurement = {
    "station_id": 1,
    "aircraft_id": 1,
    "noise_level_db": 72.5,
    "timestamp": "2026-11-13T12:30:00+01:00"
}


def test_post_measurement_invalid_station(client_with_measurements):
    data = {**valid_measurement, "station_id": 999}

    response = client_with_measurements.post(
        "/api/measurements",
        json=data
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Station not found"


def test_post_measurement_invalid_aircraft(client_with_measurements):
    data = {**valid_measurement, "aircraft_id": 999}

    response = client_with_measurements.post(
        "/api/measurements",
        json=data
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Aircraft not found"


def test_post_measurement_negative_noise(client_with_measurements):
    data = {**valid_measurement, "noise_level_db": -10}

    response = client_with_measurements.post(
        "/api/measurements",
        json=data
    )

    assert response.status_code == 422


def test_post_measurement_missing_field(client_with_measurements):
    data = {
        "station_id": 1,
        "aircraft_id": 1,
        "timestamp": "2026-11-13T12:30:00+01:00"
    }

    response = client_with_measurements.post(
        "/api/measurements",
        json=data
    )

    assert response.status_code == 422


def test_post_measurement_success(client_with_measurements):
    data = {
        "station_id": 1,
        "aircraft_id": 1,
        "noise_level_db": 72.5,
        "timestamp": "2026-11-13T12:30:00+01:00"
    }

    response = client_with_measurements.post(
        "/api/measurements",
        json=data
    )

    assert response.status_code == 201

    created = response.json()

    assert created["station_id"] == 1
    assert created["aircraft_id"] == 1
    assert created["noise_level_db"] == 72.5
    assert "id" in created


def test_post_measurement_is_stored(client_with_measurements):
    data = {
        "station_id": 1,
        "aircraft_id": 1,
        "noise_level_db": 72.5,
        "timestamp": "2026-11-13T12:30:00+01:00"
    }

    client_with_measurements.post(
        "/api/measurements",
        json=data
    )

    response = client_with_measurements.get(
        "/api/measurements?station_id=1"
    )

    results = response.json()

    assert len(results) == 3
    assert any(m["noise_level_db"] == 72.5 for m in results)
