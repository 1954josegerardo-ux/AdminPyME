@echo off
python -m venv venv
echo .\venv\Scripts\Activate.ps1
echo (venv) PS C:\proyecto3>
python -m pip install --upgrade pip
python pip install pandas google-generativeai openpyxl
python pip list | Select-String "pandas|google-generativeai"
python pip install Pillow 
echo.
echo Instalacion completa.
echo.