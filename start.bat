@echo off
echo Starting InstaHub MVP...
echo.
echo Make sure MongoDB is running on mongodb://localhost:27017
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000


