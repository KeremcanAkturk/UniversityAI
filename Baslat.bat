@echo off
cd /d "%~dp0"

echo Bot baslatiliyor...
echo -------------------------------------

:: "sistem" klasöründeki python'u kullanarak, ana klasördeki app.py'yi aç
start "" "%~dp0sistem\python.exe" -m streamlit run "%~dp0app.py"

exit