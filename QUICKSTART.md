# 🚀 Guia de Início Rápido

## Instalação em 3 Passos

### 1. Configurar Ambiente

```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar configurações (importante!)
nano .env
```

**Configurações Essenciais:**
- `AUTO_MODE=true` - Publicação automática (ou false para revisão manual)
- `CYCLE_MINUTES=10` - Intervalo entre varreduras
- `MOCK_EXTERNAL_APIS=true` - Use true para testar sem APIs reais

### 2. Iniciar com Docker (Recomendado)

```bash
# Tornar script executável
chmod +x start.sh

# Iniciar sistema
./start.sh
```

Ou manualmente:

```bash
docker-compose up -d --build
```

### 3. Acompanhar Logs

```bash
# Ver logs em tempo real
docker-compose logs -f

# Apenas do sistema principal
docker-compose logs -f receira
```

---

## Instalação Manual (Sem Docker)

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
nano .env

# Executar
python src/main.py
```

---

## Como Funciona

O sistema opera em **ciclos contínuos**:

```
┌─────────────────────────────────────────────────┐
│  CICLO (a cada X minutos)                       │
├─────────────────────────────────────────────────┤
│  1. MONITORAMENTO                               │
│     ├── TikTok (hashtags + trending)            │
│     ├── Instagram (reels + explore)             │
│     └── RSS (feeds configurados)                │
│                                                  │
│  2. DETECÇÃO VIRAL                              │
│     └── Multi-signal: views, likes, shares      │
│                                                  │
│  3. PROCESSAMENTO                               │
│     ├── Extração de dados                       │
│     ├── Reescrita profissional                  │
│     ├── Normalização de ingredientes            │
│     └── Enriquecimento (SEO, social, etc)       │
│                                                  │
│  4. DEDUPLICAÇÃO                                │
│     └── Fingerprinting + similaridade           │
│                                                  │
│  5. PUBLICAÇÃO                                  │
│     ├── AUTO_MODE=true → Publica automaticamente│
│     └── AUTO_MODE=false → Envia para aprovação  │
└─────────────────────────────────────────────────┘
```

---

## Testando o Sistema

### Modo Mock (Desenvolvimento)

No `.env`, configure:

```bash
MOCK_EXTERNAL_APIS=true
CYCLE_MINUTES=1
```

Isso gerará dados fictícios para testar a pipeline completa sem depender de APIs externas.

### Verificar Logs

```bash
# Logs gerais
tail -f logs/app.log

# Logs de monitoramento
tail -f logs/monitors.log

# Logs de processamento
tail -f logs/processors.log

# Apenas erros
tail -f logs/errors.log
```

---

## Configurações Importantes

### Thresholds de Viralização

```bash
THRESHOLD_VIRAL_VIEWS=100000     # Mínimo de views
THRESHOLD_VIRAL_LIKES=5000       # Mínimo de likes
THRESHOLD_VIRAL_SHARES=500       # Mínimo de shares
THRESHOLD_GROWTH_RATE=50         # % crescimento
TIME_WINDOW_HOURS=6              # Janela temporal
```

**Dica:** Para testar, use valores menores (ex: 10000, 500, 50).

### Modo de Operação

```bash
# AUTOMÁTICO (publica sozinho)
AUTO_MODE=true

# MANUAL (envia para aprovação)
AUTO_MODE=false
```

### Integração com APIs

```bash
# TikTok
TIKTOK_API_KEY=your_key_here

# Instagram
INSTAGRAM_GRAPH_API_TOKEN=your_token_here

# RSS Feeds
RSS_FEED_URLS=https://feed1.com/rss,https://feed2.com/rss
```

---

## Comandos Úteis

```bash
# Ver status
docker-compose ps

# Parar sistema
docker-compose down

# Reiniciar
docker-compose restart

# Ver logs das últimas 100 linhas
docker-compose logs --tail=100 receira

# Acessar container
docker-compose exec receira bash

# Limpar tudo e recomeçar
docker-compose down -v
rm -rf data/ logs/
./start.sh
```

---

## Estrutura de Dados (JSON Output)

Cada receita processada gera:

```json
{
  "title": "Bolo de Chocolate Viral 3 Ingredientes",
  "slug": "bolo-chocolate-viral-3-ingredientes",
  "source": {
    "type": "tiktok",
    "profile": "@chefviral",
    "url": "https://tiktok.com/@chefviral/video/123"
  },
  "media": {
    "media_type": "video",
    "media_url": "https://..."
  },
  "trend_metrics": {
    "views": 2500000,
    "likes": 150000,
    "shares": 25000,
    "growth_rate_percent": 320
  },
  "ingredients": [...],
  "instructions": [...],
  "publish_recommendation": {
    "publish": true,
    "priority": "viral"
  }
}
```

---

## Troubleshooting

### Sistema não detecta receitas virais

- Reduza os thresholds em `.env`
- Verifique se `MOCK_EXTERNAL_APIS=true` para testar
- Veja logs: `docker-compose logs -f`

### Receitas duplicadas

- Ajuste `DUPLICATE_THRESHOLD` (padrão: 0.9)
- Valores menores = mais rigoroso

### Erros de API

- Configure `MOCK_EXTERNAL_APIS=true` para desenvolvimento
- Verifique credenciais das APIs
- TikTok/Instagram podem ter rate limits

---

## Próximos Passos

1. **Integrar com seu CMS:** Configure `CMS_ENDPOINT` e `CMS_API_KEY`
2. **Configurar APIs reais:** Obtenha tokens do TikTok/Instagram
3. **Adicionar RSS Feeds:** Liste URLs em `RSS_FEED_URLS`
4. **Ajustar thresholds:** Baseado no seu nicho
5. **Monitorar métricas:** Implementar dashboard de analytics

---

## Suporte

- 📖 Documentação completa: `README.md`
- 🐛 Issues: Abra uma issue no repositório
- 📧 Email: [seu-email]

---

**⚠️ Importante:** Este sistema deve respeitar os Termos de Serviço das plataformas. Use responsavelmente e sempre atribua fontes originais.
