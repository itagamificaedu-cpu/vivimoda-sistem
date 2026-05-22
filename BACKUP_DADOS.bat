@echo off
chcp 65001 >nul
title VIVIMODA - Backup dos Dados

cd /d "%~dp0"

:: Cria pasta de backup com data de hoje
for /f "tokens=1-3 delims=/" %%a in ("%date%") do (
    set DIA=%%a
    set MES=%%b
    set ANO=%%c
)
set PASTA_BACKUP=%USERPROFILE%\Desktop\BACKUP_VIVIMODA_%DIA%-%MES%-%ANO%

echo.
echo  ===================================
echo   VIVIMODA - Backup dos Dados
echo  ===================================
echo.
echo  Destino: %PASTA_BACKUP%
echo.

mkdir "%PASTA_BACKUP%" 2>nul

:: Copia banco de dados SQLite
if exist "db_local_teste.sqlite3" (
    copy /Y "db_local_teste.sqlite3" "%PASTA_BACKUP%\banco_de_dados.sqlite3" >nul
    echo  [OK] Banco de dados copiado
) else (
    echo  [AVISO] Banco de dados nao encontrado
)

:: Copia pasta de midias (fotos de produtos, etc.)
if exist "media\" (
    xcopy /E /I /Y /Q "media" "%PASTA_BACKUP%\media" >nul
    echo  [OK] Arquivos de midia copiados
)

echo.
echo  ===================================
echo   Backup salvo em:
echo   %PASTA_BACKUP%
echo.
echo   Guarde esta pasta em um pen drive
echo   ou servico de nuvem (Google Drive,
echo   Dropbox, etc.) para seguranca!
echo  ===================================
echo.

:: Abre a pasta de backup
start "" "%PASTA_BACKUP%"

pause
