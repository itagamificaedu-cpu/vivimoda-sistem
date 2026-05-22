@echo off
chcp 65001 >nul
title VIVIMODA - Parar Servidor

echo.
echo  ===================================
echo   VIVIMODA - Parando servidor...
echo  ===================================
echo.

:: Para todos os processos Python que estejam rodando o servidor
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1

:: Verifica se parou
timeout /t 1 /nobreak >nul
netstat -an | find "0.0.0.0:8000" >nul 2>&1
if %errorLevel% == 1 (
    echo  Servidor parado com sucesso.
) else (
    echo  [AVISO] Ainda pode haver processo rodando.
    echo  Aguarde alguns segundos e tente novamente.
)

echo.
echo  Para iniciar novamente, clique no atalho "VIVIMODA Sistema"
echo  na area de trabalho.
echo.
timeout /t 3 /nobreak >nul
