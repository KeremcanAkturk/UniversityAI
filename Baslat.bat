@echo off
cd /d "%~dp0"

:: "start" komutunu sildik, artık direkt çalışacak (VBS bunu gizleyecek)
"%~dp0sistem\python.exe" -m streamlit run "%~dp0app.py"