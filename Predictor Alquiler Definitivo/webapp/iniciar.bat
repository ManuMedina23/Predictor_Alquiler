@echo off
SETLOCAL

REM Ruta al entorno virtual
SET VENV_DIR=..\.venv

REM Activar entorno virtual
CALL "%VENV_DIR%\Scripts\activate.bat"
echo Entorno virtual activado.

REM Ejecutar Streamlit
echo  Ejecutando Streamlit...
streamlit run Inicio.py

ENDLOCAL
