@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title VIVIMODA - Instalador do Sistema

:: ================================================================
::  VIVIMODA ConfecSystem — INSTALADOR COMPLETO
::  Execute este arquivo UMA VEZ para instalar tudo.
::  Depois use o atalho "VIVIMODA Sistema" na area de trabalho.
:: ================================================================

:: --- Precisa de Administrador para criar tarefa de inicializacao ---
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo  Solicitando permissao de Administrador...
    echo  Clique SIM na janela que aparecer.
    echo.
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

cls
echo.
echo  ================================================================
echo.
echo    VIVIMODA - Sistema de Gestao de Confeccoes
echo    Instalacao Completa
echo.
echo  ================================================================
echo.
echo  Por favor aguarde. Isso pode levar de 3 a 5 minutos.
echo.

cd /d "%~dp0"
set PASTA=%~dp0
set DJANGO_SETTINGS=confec_system.settings.local_sqlite

:: ================================================================
:: ETAPA 1 — Localizar Python
:: ================================================================
echo  [1/7] Localizando Python...

set PYTHON=

:: Procura nas pastas mais comuns (do mais novo para o mais velho)
for %%v in (314 313 312 311 310 39) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%v\python.exe" (
        set PYTHON=%LOCALAPPDATA%\Programs\Python\Python%%v\python.exe
        goto :python_ok
    )
    if exist "C:\Python%%v\python.exe" (
        set PYTHON=C:\Python%%v\python.exe
        goto :python_ok
    )
)

:: Tenta PATH
python --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "delims=" %%i in ('where python') do (
        set PYTHON=%%i
        goto :python_ok
    )
)

:: Python nao encontrado — tenta instalar via winget (Windows 10/11)
echo.
echo  Python nao encontrado. Instalando Python 3.11...
echo  (Requer conexao com a internet para esta etapa)
echo.
winget install --id Python.Python.3.11 -e --source winget --accept-package-agreements --accept-source-agreements --silent
if %errorLevel% == 0 (
    set PYTHON=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
    :: Refresca PATH
    call refreshenv >nul 2>&1
    goto :python_ok
)

echo.
echo  ============================================================
echo   [ERRO] Python nao foi encontrado nem instalado.
echo.
echo   Por favor:
echo   1. Acesse: https://www.python.org/downloads/
echo   2. Baixe e instale Python 3.11 ou mais novo
echo   3. IMPORTANTE: marque "Add Python to PATH"
echo   4. Reinicie o computador
echo   5. Execute este instalador novamente
echo  ============================================================
echo.
pause
exit /b 1

:python_ok
echo     Python encontrado: %PYTHON%
echo.

:: Salva o caminho do Python para os outros scripts usarem
echo %PYTHON%> "%PASTA%python_path.txt"

:: ================================================================
:: ETAPA 2 — Instalar dependencias
:: ================================================================
echo  [2/7] Instalando pacotes Python (aguarde)...

"%PYTHON%" -m pip install --quiet --upgrade pip 2>nul

"%PYTHON%" -m pip install --quiet ^
    Django ^
    djangorestframework ^
    django-filter ^
    celery==5.4.0 ^
    django-celery-beat ^
    django-celery-results ^
    python-decouple ^
    validate-docbr ^
    crispy-bootstrap5 ^
    django-crispy-forms ^
    pytz ^
    whitenoise ^
    Pillow ^
    django-cors-headers ^
    openpyxl ^
    reportlab

if %errorLevel% neq 0 (
    echo.
    echo  [AVISO] Alguns pacotes podem nao ter instalado corretamente.
    echo  Continuando...
    echo.
)

echo     Pacotes instalados!
echo.

:: ================================================================
:: ETAPA 3 — Criar banco de dados
:: ================================================================
echo  [3/7] Criando banco de dados...

"%PYTHON%" manage.py migrate --settings=%DJANGO_SETTINGS% 2>&1

if %errorLevel% neq 0 (
    echo.
    echo  [ERRO] Falha ao criar banco de dados.
    echo  Verifique se a pasta do sistema tem permissao de escrita.
    pause
    exit /b 1
)
echo     Banco de dados criado!
echo.

:: ================================================================
:: ETAPA 4 — Criar administrador
:: ================================================================
echo  [4/7] Criando usuario administrador...
"%PYTHON%" manage.py criar_admin --settings=%DJANGO_SETTINGS% 2>&1
echo     Administrador criado!
echo.

:: ================================================================
:: ETAPA 5 — Carregar dados de demonstracao
:: ================================================================
echo  [5/7] Carregando dados iniciais...
"%PYTHON%" manage.py carregar_fixtures --settings=%DJANGO_SETTINGS% 2>&1
echo     Dados carregados!
echo.

:: Coleta arquivos estaticos
"%PYTHON%" manage.py collectstatic --noinput --settings=%DJANGO_SETTINGS% >nul 2>&1
echo.

:: ================================================================
:: ETAPA 6 — Criar atalho na Area de Trabalho
:: ================================================================
echo  [6/7] Criando atalho na area de trabalho...

:: Cria o script VBS de abertura silenciosa
call :criar_vbs

:: Cria o atalho .lnk na Area de Trabalho de todos os usuarios
set DESKTOP_PUBLICO=C:\Users\Public\Desktop
set DESKTOP_USER=%USERPROFILE%\Desktop

powershell -Command ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "$s = $ws.CreateShortcut('%DESKTOP_PUBLICO%\VIVIMODA Sistema.lnk');" ^
  "$s.TargetPath = 'wscript.exe';" ^
  "$s.Arguments = '/nologo ""%PASTA%VIVIMODA.vbs""';" ^
  "$s.WorkingDirectory = '%PASTA%';" ^
  "$s.Description = 'Abrir sistema VIVIMODA';" ^
  "$s.WindowStyle = 7;" ^
  "$s.Save();" 2>nul

:: Tambem cria na area de trabalho do usuario atual
powershell -Command ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "$s = $ws.CreateShortcut('%DESKTOP_USER%\VIVIMODA Sistema.lnk');" ^
  "$s.TargetPath = 'wscript.exe';" ^
  "$s.Arguments = '/nologo ""%PASTA%VIVIMODA.vbs""';" ^
  "$s.WorkingDirectory = '%PASTA%';" ^
  "$s.Description = 'Abrir sistema VIVIMODA';" ^
  "$s.WindowStyle = 7;" ^
  "$s.Save();" 2>nul

echo     Atalho criado!
echo.

:: ================================================================
:: ETAPA 7 — Inicializacao automatica com Windows
:: ================================================================
echo  [7/7] Configurando inicio automatico com Windows...

:: Cria tarefa no Agendador de Tarefas
schtasks /Delete /TN "VIVIMODA Sistema" /F >nul 2>&1
schtasks /Create ^
  /TN "VIVIMODA Sistema" ^
  /TR "wscript.exe /nologo \"%PASTA%iniciar_servidor.vbs\"" ^
  /SC ONLOGON ^
  /RL HIGHEST ^
  /F >nul 2>&1

if %errorLevel% == 0 (
    echo     Inicio automatico configurado!
) else (
    echo     [AVISO] Nao foi possivel configurar inicio automatico.
    echo     O sistema precisara ser iniciado manualmente.
)
echo.

:: ================================================================
:: CONCLUIDO
:: ================================================================
cls
echo.
echo  ================================================================
echo.
echo    VIVIMODA instalado com sucesso!
echo.
echo  ================================================================
echo.
echo   COMO USAR DIARIAMENTE:
echo   - Clique duplo no icone "VIVIMODA Sistema" na area de trabalho
echo   - O navegador abre automaticamente na tela de login
echo.
echo   ACESSO AO SISTEMA:
echo   - Endereco: http://localhost:8000
echo   - Login:    admin
echo   - Senha:    confec@2024
echo.
echo   INICIO AUTOMATICO:
echo   - O sistema ja inicia junto com o Windows
echo   - Aguarde ~5 segundos apos ligar o computador
echo.
echo  ================================================================
echo.

choice /C SN /M "Deseja abrir o sistema agora (S/N)? "
if %errorLevel% == 1 (
    start "" wscript.exe /nologo "%PASTA%VIVIMODA.vbs"
)

echo.
echo  Instalacao concluida. Esta janela pode ser fechada.
pause
exit /b 0


:: ================================================================
:: SUBROTINA: Cria os arquivos VBS
:: ================================================================
:criar_vbs

:: --- VIVIMODA.vbs: Inicia servidor + abre navegador (sem janela CMD) ---
(
echo ' VIVIMODA - Iniciador silencioso do sistema
echo ' Duplo clique para abrir o sistema no navegador
echo.
echo Option Explicit
echo Dim objShell, objFSO, strPasta, strPython, strCmd
echo.
echo Set objShell = CreateObject^("WScript.Shell"^)
echo Set objFSO   = CreateObject^("Scripting.FileSystemObject"^)
echo.
echo strPasta = objFSO.GetParentFolderName^(WScript.ScriptFullName^)
echo.
echo ' Le o caminho do Python salvo pelo instalador
echo Dim strArqPython
echo strArqPython = strPasta ^& "\python_path.txt"
echo If objFSO.FileExists^(strArqPython^) Then
echo     Dim oArq
echo     Set oArq = objFSO.OpenTextFile^(strArqPython, 1^)
echo     strPython = Trim^(oArq.ReadLine^(^)^)
echo     oArq.Close
echo Else
echo     strPython = "python"
echo End If
echo.
echo ' Verifica se servidor ja esta rodando
echo Dim bRodando
echo bRodando = False
echo On Error Resume Next
echo Dim oHTTP
echo Set oHTTP = CreateObject^("MSXML2.XMLHTTP"^)
echo oHTTP.open "GET", "http://localhost:8000/auth/login/", False
echo oHTTP.send
echo If oHTTP.status ^> 0 Then bRodando = True
echo On Error GoTo 0
echo.
echo ' Se nao estiver rodando, inicia o servidor
echo If Not bRodando Then
echo     strCmd = "cmd /c cd /d """ ^& strPasta ^& """ ^&^& """ ^& strPython ^& """ manage.py runserver 0.0.0.0:8000 --settings=confec_system.settings.local_sqlite"
echo     objShell.Run strCmd, 0, False
echo     WScript.Sleep 3500
echo End If
echo.
echo ' Abre o navegador padrao
echo objShell.Run "http://localhost:8000", 1, False
) > "%PASTA%VIVIMODA.vbs"

:: --- iniciar_servidor.vbs: Usado pelo Agendador de Tarefas (so inicia, nao abre navegador) ---
(
echo ' VIVIMODA - Inicia servidor ao ligar o Windows
echo Option Explicit
echo Dim objShell, objFSO, strPasta, strPython, strCmd
echo Set objShell = CreateObject^("WScript.Shell"^)
echo Set objFSO   = CreateObject^("Scripting.FileSystemObject"^)
echo strPasta = objFSO.GetParentFolderName^(WScript.ScriptFullName^)
echo Dim strArqPython
echo strArqPython = strPasta ^& "\python_path.txt"
echo If objFSO.FileExists^(strArqPython^) Then
echo     Dim oArq
echo     Set oArq = objFSO.OpenTextFile^(strArqPython, 1^)
echo     strPython = Trim^(oArq.ReadLine^(^)^)
echo     oArq.Close
echo Else
echo     strPython = "python"
echo End If
echo strCmd = "cmd /c cd /d """ ^& strPasta ^& """ ^&^& """ ^& strPython ^& """ manage.py runserver 0.0.0.0:8000 --settings=confec_system.settings.local_sqlite"
echo objShell.Run strCmd, 0, False
) > "%PASTA%iniciar_servidor.vbs"

goto :eof
