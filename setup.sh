#!/bin/bash

# Script de configuração inicial do projeto

echo "🔧 Configuração Inicial do Sistema de Receitas Virais"
echo "======================================================"
echo ""

# 1. Verificar Python
echo "1️⃣  Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "   ❌ Python 3 não encontrado. Instale Python 3.9+ primeiro."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "   ✓ Python $PYTHON_VERSION encontrado"
echo ""

# 2. Criar ambiente virtual
echo "2️⃣  Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✓ Ambiente virtual criado"
else
    echo "   ⚠️  Ambiente virtual já existe"
fi
echo ""

# 3. Ativar e instalar dependências
echo "3️⃣  Instalando dependências..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "   ✓ Dependências instaladas"
echo ""

# 4. Criar arquivo .env
echo "4️⃣  Configurando variáveis de ambiente..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   ✓ Arquivo .env criado"
    echo "   ⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações!"
else
    echo "   ⚠️  Arquivo .env já existe (não sobrescrito)"
fi
echo ""

# 5. Criar diretórios
echo "5️⃣  Criando diretórios..."
mkdir -p data logs data/media data/cache
echo "   ✓ Diretórios criados"
echo ""

# 6. Verificar configuração
echo "6️⃣  Verificando configuração..."
if grep -q "MOCK_EXTERNAL_APIS=true" .env; then
    echo "   ✓ Modo MOCK ativado (bom para testes)"
else
    echo "   ⚠️  Modo MOCK desativado - configure APIs reais"
fi
echo ""

# 7. Resumo
echo "======================================================"
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo "======================================================"
echo ""
echo "📝 Próximos passos:"
echo ""
echo "1. Ative o ambiente virtual:"
echo "   source venv/bin/activate"
echo ""
echo "2. Edite o arquivo .env com suas configurações:"
echo "   nano .env"
echo ""
echo "3. Execute o teste rápido:"
echo "   python test_quick.py"
echo ""
echo "4. Inicie o sistema:"
echo "   python src/main.py"
echo ""
echo "   OU com Docker:"
echo "   ./start.sh"
echo ""
echo "📚 Documentação:"
echo "   - README.md          : Documentação completa"
echo "   - QUICKSTART.md      : Guia de início rápido"
echo "   - EXAMPLES.md        : Exemplos de output JSON"
echo ""
echo "🐛 Suporte:"
echo "   - Logs: logs/app.log"
echo "   - Erros: logs/errors.log"
echo ""
