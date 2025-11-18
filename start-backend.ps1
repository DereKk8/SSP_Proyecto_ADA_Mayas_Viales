# Start the FastAPI backend server
Write-Host "Starting FastAPI backend..." -ForegroundColor Green

Set-Location backend
C:/Users/tomas/Downloads/6to_semestre/analisis/proyecto/.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
