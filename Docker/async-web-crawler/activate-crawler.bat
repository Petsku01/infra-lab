@echo off
where docker-compose >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Docker Compose not found. Install Docker Desktop.
    exit /b 1
)

if not exist output mkdir output
docker-compose up --build
