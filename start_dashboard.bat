@echo off
echo Starting Comprehensive Project Management Dashboard...
echo.
echo This will automatically open your browser to the dashboard.
echo.

cd /d "C:\Users\srira\OneDrive\Desktop\Projects\Tetakisu\Version - 2\budgeting_project"

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting Streamlit dashboard...
echo Dashboard will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

start http://localhost:8501
streamlit run streamlit_app.py --server.address=127.0.0.1 --server.port=8501

pause
