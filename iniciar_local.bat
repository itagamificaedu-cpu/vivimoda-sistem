@echo off
:: ============================================================
::  ConfecSystem — Inicializador Local (Windows)
::  Usa SQLite, sem Docker, sem PostgreSQL, sem Redis
:: ============================================================
chcp 65001 >nul
setlocal

echo.
echo  ===================================================
echo   VIVIMODA - ConfecSystem - Teste Local
echo  ===================================================
echo.

:: Muda para o diretório do script
cd /d "%~dp0"

:: Caminho do Python 3.14 (instalado na maquina)
set PYTHON=%LOCALAPPDATA%\Programs\Python\Python314\python.exe
set PIP=%LOCALAPPDATA%\Programs\Python\Python314\Scripts\pip.exe
set DJANGO_SETTINGS=confec_system.settings.local_sqlite

if not exist "%PYTHON%" (
    echo  [AVISO] Python 3.14 nao encontrado no local padrao.
    echo  Procurando outras versoes...

    for %%p in (
        "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        "C:\Python313\python.exe"
        "C:\Python312\python.exe"
    ) do (
        if exist %%p (
            set PYTHON=%%p
            goto :python_ok
        )
    )

    echo.
    echo  [ERRO] Python nao encontrado!
    echo  Instale em: https://www.python.org/downloads/
    echo  Marque "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)

:python_ok
echo  Python: %PYTHON%
echo.

:: Instala pacotes que faltam
echo  Verificando/instalando dependencias...
"%PIP%" install --quiet --upgrade pip 2>nul

"%PIP%" install --quiet ^
    django-filter ^
    celery==5.4.0 ^
    django-celery-beat ^
    django-celery-results ^
    python-decouple ^
    validate-docbr ^
    crispy-bootstrap5 ^
    pytz

echo  Dependencias prontas!
echo.

:: Roda as migrations
echo  Criando banco de dados SQLite...
"%PYTHON%" manage.py migrate --settings=%DJANGO_SETTINGS% 2>&1
echo.

:: Cria admin
echo  Criando usuario administrador...
"%PYTHON%" manage.py criar_admin --settings=%DJANGO_SETTINGS% 2>&1
echo.

:: Carrega fixtures de dados demo
echo  Carregando dados de demonstracao...
"%PYTHON%" manage.py carregar_fixtures --settings=%DJANGO_SETTINGS% 2>&1
echo.

:: Coleta estáticos
echo  Preparando arquivos estaticos...
"%PYTHON%" manage.py collectstatic --noinput --settings=%DJANGO_SETTINGS% >nul 2>&1

echo.
echo  ===================================================
echo   Tudo pronto! Abrindo no navegador...
echo  ===================================================
echo.
echo   Acesso: http://localhost:8000
echo   Login:  admin
echo   Senha:  confec@2024
echo.
echo   Para parar: feche esta janela ou pressione Ctrl+C
echo  ===================================================
echo.

:: Abre o navegador após 3 segundos
start "" /B cmd /C "timeout /t 3 /nobreak >nul && start http://localhost:8000"

:: Inicia o servidor de desenvolvimento
"%PYTHON%" manage.py runserver 0.0.0.0:8000 --settings=%DJANGO_SETTINGS%

pause
