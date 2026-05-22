# Imagem base Python 3.11 Alpine — mais leve e confiável em VPS
FROM python:3.11-alpine

# Evita geração de .pyc e habilita log em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema via apk (Alpine)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    cairo \
    pango \
    gdk-pixbuf \
    jpeg-dev \
    libpng-dev \
    freetype-dev \
    curl

WORKDIR /app

# Copia e instala dependências Python primeiro (otimiza cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do projeto
COPY . .

# Cria diretórios necessários
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Coleta arquivos estáticos
RUN python manage.py collectstatic --noinput --settings=confec_system.settings.production || true

EXPOSE 8000

# Inicia com Gunicorn em produção
CMD ["gunicorn", "confec_system.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
