# Aircraft Noise Monitoring

A full-stack web application for monitoring aircraft noise measurements at monitoring stations.

## Architecture

- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Backend:** Python, FastAPI
- **Database:** SQLite with SQLModel
- **Web server / Reverse proxy:** Nginx
- **Containerization:** Docker and Docker Compose

## Requirements

- Docker Desktop
- Git (if cloning the repository)

## Getting Started with Docker

### 1. Clone the repository

```bash
git clone https://github.com/rreateguia/aircraft-noise-monitor.git
cd aircraft-noise-monitor
```

### 2. Start the application

```bash
docker compose up --build -d
```

This builds and starts the frontend and backend containers.

### 3. Access the application

| Service | URL |
|---|---|
| Frontend | http://localhost:8080 |
| Backend API | http://localhost:8000 |
| API documentation (Swagger) | http://localhost:8000/docs |
| Measurements endpoint | http://localhost:8080/api/measurements |

### 4. Stop the application

```bash
docker compose down
```

To stop the containers without deleting the database, use the command above.

**Database persistence:** SQLite data is stored in a named Docker volume (`aircraft_noise_data`). The data remains available when containers are stopped or recreated.

To remove the containers AND the database volume:

```bash
docker compose down -v
```

## Backend Development Without Docker

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate it (Windows PowerShell)

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
cd backend
python -m pip install -r requirements.txt
```

### 4. Start the backend

```bash
fastapi dev main.py
```

Open http://127.0.0.1:8000/docs to access the interactive API documentation.

## Project Structure

```text
aircraft-noise-monitor/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── requirements.txt
│   └── tests/
│
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   ├── Dockerfile
│   └── nginx.conf
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── README.md
```

## Testing

Run the backend tests from the `backend` directory:

```bash
python -m pytest -q
```
