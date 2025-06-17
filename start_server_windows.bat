@echo off
echo 🌍 Starting EcoTrack Ghana API Server...

cd /d "c:\Users\Abigail Adwoa Agbesi\Desktop\GhanaClean\EcoTrackAPI"

REM Set environment variables
set PYTHONPATH=%CD%
set ENVIRONMENT=development
set DEBUG=true

echo 🚀 Starting server on http://localhost:8000
echo 📝 API docs available at http://localhost:8000/docs
echo 👨‍💼 Admin panel at http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start uvicorn with single worker to avoid Windows multiprocessing issues
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --workers 1

pause
