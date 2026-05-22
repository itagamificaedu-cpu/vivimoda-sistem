#!/bin/bash
# Script de setup completo — sobe o ConfecSystem com um comando
set -e

echo "============================================"
echo "   ConfecSystem — Setup Inicial"
echo "============================================"

# Verifica se .env existe; se não, cria a partir do exemplo
if [ ! -f .env ]; then
    echo "Criando .env a partir do .env.example..."
    cp .env.example .env
    echo "  ATENÇÃO: Edite o arquivo .env com suas configurações antes de continuar!"
fi

echo ""
echo "1. Subindo os containers Docker..."
docker-compose up -d --build

echo ""
echo "2. Aguardando o banco de dados ficar pronto..."
sleep 10

echo ""
echo "3. Rodando migrations..."
docker-compose exec web python manage.py migrate --settings=confec_system.settings.development

echo ""
echo "4. Criando superusuário padrão (admin / confec@2024)..."
docker-compose exec web python manage.py criar_admin --settings=confec_system.settings.development

echo ""
echo "5. Carregando dados de exemplo (fixtures)..."
docker-compose exec web python manage.py carregar_fixtures --settings=confec_system.settings.development

echo ""
echo "6. Coletando arquivos estáticos..."
docker-compose exec web python manage.py collectstatic --noinput --settings=confec_system.settings.development

echo ""
echo "============================================"
echo "   ConfecSystem instalado com sucesso!"
echo "============================================"
echo ""
echo "  Acesse: http://localhost"
echo "  Admin:  http://localhost/admin"
echo "  Login:  admin / confec@2024"
echo ""
echo "  Para parar: docker-compose down"
echo "  Para logs:  docker-compose logs -f web"
echo ""
