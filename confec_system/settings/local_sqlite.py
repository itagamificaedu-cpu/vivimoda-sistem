"""
Configurações para TESTE LOCAL com SQLite.
Não precisa de PostgreSQL, Redis nem Docker.
Use apenas para testar/demonstrar o sistema localmente.

Uso:
    python manage.py runserver --settings=confec_system.settings.local_sqlite
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Chave secreta fixa (apenas para testes locais!)
SECRET_KEY = 'django-insecure-vivimoda-teste-local-2024-nao-usar-em-producao'

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Formulários e filtros
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'rest_framework',
    'corsheaders',

    # Celery Beat (migrations necessárias, mas não usa Redis aqui)
    'django_celery_beat',
    'django_celery_results',

    # Apps do projeto
    'apps.core',
    'apps.autenticacao',
    'apps.configuracoes',
    'apps.funcionarios',
    'apps.clientes',
    'apps.fornecedores',
    'apps.produtos',
    'apps.estoque',
    'apps.compras',
    'apps.financeiro',
    'apps.caixa',
    'apps.vendas',
    'apps.carne',
    'apps.relatorios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.autenticacao.middleware.AuditoriaMiddleware',
]

ROOT_URLCONF = 'confec_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.dados_globais',
            ],
        },
    },
]

WSGI_APPLICATION = 'confec_system.wsgi.application'

# ── Banco de dados: SQLite (sem instalação extra) ────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_local_teste.sqlite3',
    }
}

# Model de usuário customizado
AUTH_USER_MODEL = 'autenticacao.Usuario'
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/auth/login/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
]

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Fortaleza'
USE_I18N = True
USE_TZ = True

# Arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Arquivos de mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Cache: memória local (sem Redis) ────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Sessão via banco (sem Redis)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 28800

# ── Celery: desabilitado para teste local ───────────────────────────────────
CELERY_TASK_ALWAYS_EAGER = True   # Executa tarefas de forma síncrona (sem worker)
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# E-mail no console (não envia de verdade)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.PaginacaoPadrao',
    'PAGE_SIZE': 25,
}

LISTAGEM_ITENS_POR_PAGINA = 25
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
TENTATIVAS_LOGIN_MAX = 5
BLOQUEIO_LOGIN_MINUTOS = 30
SITE_NAME = 'ConfecSystem (Teste Local)'

# Log simplificado no console
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'WARNING'},
    'loggers': {
        'django.request': {'handlers': ['console'], 'level': 'ERROR'},
        'apps': {'handlers': ['console'], 'level': 'INFO'},
    },
}
