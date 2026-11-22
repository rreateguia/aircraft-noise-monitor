
# 1. Start with an official Python image
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the Python dependencies file
COPY backend/requirements.txt .

# 4. Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the backend source code
COPY backend/ .

# 6. Make port 8000 available
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/').read()"

# 7. Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
