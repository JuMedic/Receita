#!/bin/bash

# Script de inicialização rápida

echo "🍳 Sistema de Receitas Virais - Inicialização"
echo "=============================================="

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado. Criando a partir do .env.example..."
    cp .env.example .env
    echo "✓ Arquivo .env criado. Por favor, configure as variáveis antes de continuar."
    exit 1
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p data logs data/media data/cache config

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Construir e iniciar
echo "🚀 Construindo e iniciando containers..."
docker-compose up -d --build

echo ""
echo "✅ Sistema iniciado!"
echo ""
echo "📊 Comandos úteis:"
echo "  - Ver logs:        docker-compose logs -f"
echo "  - Parar:           docker-compose down"
echo "  - Reiniciar:       docker-compose restart"
echo "  - Status:          docker-compose ps"
echo ""
echo "🌐 API disponível em: http://localhost:${API_PORT:-8080}"
echo ""
