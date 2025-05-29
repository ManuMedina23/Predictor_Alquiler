@echo off
SETLOCAL

REM Ruta al entorno virtual
SET VENV_DIR=.venv

REM Verificar si el entorno virtual existe
IF NOT EXIST "%VENV_DIR%\Scripts\activate.bat" (
    echo Creando entorno virtual en %VENV_DIR%...
    python -m venv %VENV_DIR%
    IF ERRORLEVEL 1 (
        echo Error al crear el entorno virtual.
        EXIT /B 1
    )
)

REM Activar entorno virtual
CALL "%VENV_DIR%\Scripts\activate.bat"
echo Entorno virtual activado.

REM Actualizar pip e instalar paquetes necesarios
echo Instalando paquetes requeridos: streamlit, pandas, sqlalchemy, psycopg2...
pip install --upgrade pip
pip install -r requirements.txt
IF ERRORLEVEL 1 (
    echo  Error al instalar los paquetes.
    EXIT /B 1
)
REM Esperar confirmacion del usuario para salir
echo.
echo Paquetes instalados correctamente.
echo Presiona cualquier tecla para cerrar...
pause > nul

ENDLOCAL
