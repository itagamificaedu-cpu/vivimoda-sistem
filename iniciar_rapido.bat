@echo off
:: ============================================================
::  ConfecSystem — Inicializacao Rapida
::  Use DEPOIS de ter rodado iniciar_local.bat ao menos uma vez
:: ============================================================
chcp 65001 >nul

echo.
echo  ===================================================
echo   VIVIMODA - ConfecSystem
echo  ===================================================
echo.

cd /d "%~dp0"

set PYTHON=%LOCALAPPDATA%\Programs\Python\Python314\python.exe
set DJANGO_SETTINGS=confec_system.settings.local_sqlite

if not exist "%PYTHON%" (
    echo  [ERRO] Python nao encontrado. Execute iniciar_local.bat primeiro.
    pause
    exit /b 1
)

echo  Servidor iniciando...
echo.
echo   Acesso: http://localhost:8000
echo   Login:  admin  /  confec@2024
echo.
echo   Para parar: Ctrl+C ou feche esta janela
echo  ===================================================
echo.

start "" /B cmd /C "timeout /t 2 /nobreak >nul && start http://localhost:8000"
"%PYTHON%" manage.py runserver 0.0.0.0:8000 --settings=%DJANGO_SETTINGS%

pause
