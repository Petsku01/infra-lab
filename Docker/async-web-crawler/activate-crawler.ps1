if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Error "Docker Compose not found. Install Docker Desktop."
    exit 1
}

if (-not (Test-Path output)) {
    New-Item -ItemType Directory -Path output | Out-Null
}

docker-compose up --build
