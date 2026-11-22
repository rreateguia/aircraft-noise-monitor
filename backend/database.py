
from pathlib import Path
import os
from sqlmodel import SQLModel, Session, create_engine

# Import models so SQLModel registers all database tables
from models import Station, Aircraft, Measurement

# Store the database alongside this Python file
BASE_DIR = Path(__file__).resolve().parent

DATABASE_DIR = Path(os.getenv("DATABASE_DIR", BASE_DIR))
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

sqlite_file_name = DATABASE_DIR / "aircraft_noise.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}

engine = create_engine(
    sqlite_url,
    echo=True,
    connect_args=connect_args
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
