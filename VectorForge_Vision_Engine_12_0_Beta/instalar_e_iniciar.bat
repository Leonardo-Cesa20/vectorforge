@echo off
setlocal
title VectorForge Vision Engine 12.0
cd /d "%~dp0"

where py >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=py"
) else (
    set "PYTHON_CMD=python"
)

%PYTHON_CMD% -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :erro

%PYTHON_CMD% -m pip install --upgrade PySide6 opencv-python numpy
if errorlevel 1 goto :erro

%PYTHON_CMD% main.py
if errorlevel 1 pause
exit /b 0

:erro
echo Falha na instalacao.
echo Use Python 3.11 ou 3.12 de 64 bits.
pause
