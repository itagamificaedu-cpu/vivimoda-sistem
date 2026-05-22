# Imagem base Python 3.11 slim
FROM python:3.11-slim

# Evita geração de .pyc e habilita log em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema necessárias para WeasyPrint e Pillow
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libffi-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

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
