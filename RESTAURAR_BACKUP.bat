@echo off
chcp 65001 >nul
title VIVIMODA - Restaurar Backup

cd /d "%~dp0"

echo.
echo  ===================================================
echo   VIVIMODA - Restaurar Backup
echo  ===================================================
echo.
echo  ATENCAO: Isto substituira todos os dados atuais!
echo.
choice /C SN /M "Deseja continuar (S/N)? "
if %errorLevel% == 2 goto :cancelado

echo.
echo  Arraste o arquivo "banco_de_dados.sqlite3" do backup
echo  para esta janela e pressione ENTER:
echo.
set /p ARQUIVO_BACKUP=

:: Remove aspas se houver
set ARQUIVO_BACKUP=%ARQUIVO_BACKUP:"=%

if not exist "%ARQUIVO_BACKUP%" (
    echo.
    echo  [ERRO] Arquivo nao encontrado: %ARQUIVO_BACKUP%
    pause
    exit /b 1
)

:: Para o servidor se estiver rodando
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

:: Faz backup do atual antes de substituir
if exist "db_local_teste.sqlite3" (
    copy /Y "db_local_teste.sqlite3" "db_local_teste_ANTES_RESTAURACAO.sqlite3" >nul
    echo  [OK] Backup do banco atual salvo como db_local_teste_ANTES_RESTAURACAO.sqlite3
)

:: Restaura
copy /Y "%ARQUIVO_BACKUP%" "db_local_teste.sqlite3" >nul
if %errorLevel% == 0 (
    echo  [OK] Banco de dados restaurado com sucesso!
    echo.
    echo  Reinicie o sistema (atalho na area de trabalho).
) else (
    echo  [ERRO] Falha ao restaurar. Tente novamente.
)

pause
exit /b 0

:cancelado
echo  Operacao cancelada.
pause
