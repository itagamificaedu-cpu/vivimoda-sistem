#!/bin/bash
# Script de deploy do VIVIMODA no VPS
# Execute: bash deploy_vps.sh

set -e

REPO="https://github.com/itagamificaedu-cpu/vivimoda-sistem.git"
DIR="/app/vivimoda"

echo "=== DEPLOY VIVIMODA ==="

# Clonar ou atualizar repositório
if [ -d "$DIR" ]; then
  echo "Atualizando repositório..."
  cd "$DIR"
  git pull origin main
else
  echo "Clonando repositório..."
  git clone "$REPO" "$DIR"
  cd "$DIR"
fi

# Verificar se .env existe
if [ ! -f ".env" ]; then
  echo "ERRO: Arquivo .env não encontrado em $DIR"
  echo "Crie o .env baseado no .env.example antes de continuar"
  exit 1
fi

# Build e subir containers
echo "Build e subindo containers..."
docker compose -f docker-compose.vps.yml build vivimoda_web
docker compose -f docker-compose.vps.yml up -d

echo "=== VIVIMODA NO AR ==="
echo "Acesse: https://vivimoda.itatecnologiaeducacional.tech"
