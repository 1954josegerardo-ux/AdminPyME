@echo off
echo ============================================================
echo         INSTALADOR DE ADMINPYME
echo ============================================================
echo.
echo Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install streamlit pandas plotly pillow openpyxl
echo.
echo Instalacion completa.
echo.
echo Creando acceso directo...
echo @echo off > AdminPyME.bat
echo cd /d "%~dp0" >> AdminPyME.bat
echo start http://localhost:8501 >> AdminPyME.bat
echo python -m streamlit run app.py >> AdminPyME.bat
echo.
echo Listo. Ejecuta AdminPyME.bat para iniciar el sistema.
pause