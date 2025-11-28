# 🍳 Sistema Autônomo de Receitas Virais

Sistema 24/7 que monitora, captura e publica automaticamente receitas virais do TikTok e Instagram.

## 🎯 Funcionalidades

- **Monitoramento Contínuo**: Rastreia trends em TikTok (For You, trending sounds) e Instagram (Reels, Explore, Feed)
- **Multi-Signal Detection**: Identifica receitas virais baseado em views, shares, likes e growth rate
- **Scraping & APIs**: Suporte a scraping, APIs oficiais e RSS feeds paralelos
- **Processamento Inteligente**: Reescrita, padronização e enriquecimento automático de receitas
- **Mídia Original**: Inclui vídeos/fotos originais com atribuição de fonte
- **Deduplicação**: Sistema de fingerprinting para evitar receitas duplicadas
- **Publicação Automática**: Modo 100% autônomo ou com aprovação admin
- **Métricas & Ranking**: Tracking de engajamento e destaque automático das mais virais
- **SEO Completo**: Tags, meta descriptions e otimização automática

## 🏗️ Arquitetura

```
receira/
├── src/
│   ├── monitors/          # Scrapers TikTok, Instagram, RSS
│   ├── processors/        # Processamento e padronização
│   ├── publishers/        # Sistema de publicação
│   ├── analytics/         # Métricas e ranking
│   ├── utils/            # Utilitários (dedup, media, etc)
│   └── orchestrator/     # Loop principal 24/7
├── config/               # Configurações
├── data/                # Database e cache
├── logs/                # Logs do sistema
└── tests/               # Testes automatizados
```

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Modo de operação
AUTO_MODE=true                    # true=publicação automática, false=review admin
CYCLE_MINUTES=10                  # Intervalo entre varreduras (5-10 recomendado)

# Thresholds de viralização
THRESHOLD_VIRAL_VIEWS=100000      # Mínimo de views
THRESHOLD_VIRAL_LIKES=5000        # Mínimo de likes
THRESHOLD_VIRAL_SHARES=500        # Mínimo de shares
THRESHOLD_GROWTH_RATE=50          # % de crescimento mínimo
TIME_WINDOW_HOURS=6               # Janela temporal para análise

# Limites de filtro
MAX_INGREDIENTS_VIRAL=10          # Máximo de ingredientes
MAX_PREP_MINUTES_VIRAL=30         # Tempo máximo de preparo

# APIs (opcional)
TIKTOK_API_KEY=
INSTAGRAM_GRAPH_API_TOKEN=
RSS_FEED_URLS=url1,url2,url3

# Database
DATABASE_PATH=./data/recipes.db
CACHE_PATH=./data/cache/

# Media
MEDIA_DOWNLOAD_ENABLED=true
THUMBNAIL_GENERATION=true
```

## 🚀 Instalação

### Com Docker (Recomendado)

```bash
# Construir e iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

### Instalação Manual

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env
nano .env

# Executar
python src/main.py
```

## 📊 API & Endpoints

### Dashboard Admin (se AUTO_MODE=false)

```
GET  /admin/pending          # Receitas aguardando aprovação
POST /admin/approve/:id      # Aprovar receita
POST /admin/reject/:id       # Rejeitar receita
GET  /admin/metrics          # Métricas do sistema
```

### API Pública

```
GET  /api/recipes            # Lista receitas publicadas
GET  /api/recipes/viral      # Top receitas virais
GET  /api/recipes/:slug      # Receita específica
POST /api/recipes/:id/track  # Registrar visualização/clique
```

## 📋 Formato de Saída

Cada receita processada retorna JSON estruturado:

```json
{
  "title": "Bolo de Chocolate Viral 3 Ingredientes",
  "slug": "bolo-chocolate-viral-3-ingredientes",
  "summary": "O bolo de chocolate mais fácil do TikTok! Apenas 3 ingredientes e 15 minutos.",
  "source": {
    "type": "tiktok",
    "profile": "@chefviral",
    "name": "Chef Viral",
    "url": "https://tiktok.com/@chefviral/video/123456"
  },
  "media": {
    "media_type": "video",
    "media_url": "https://...",
    "thumbnail_frame_time": "8s",
    "media_license": "public"
  },
  "trend_metrics": {
    "views": 2500000,
    "likes": 150000,
    "shares": 25000,
    "growth_rate_percent": 320,
    "time_window_hours": 6
  },
  "category": "Doces",
  "tags": ["bolo", "tiktokfood", "receitafacil", "3ingredientes"],
  "servings": "8 porções",
  "prep_time_minutes": 5,
  "cook_time_minutes": 15,
  "total_time_minutes": 20,
  "difficulty": "Fácil",
  "estimated_cost": "R$8-15",
  "ingredients": [
    {"name": "chocolate em pó", "quantity": "200", "unit": "g"},
    {"name": "leite condensado", "quantity": "395", "unit": "g"},
    {"name": "ovos", "quantity": "3", "unit": "unidades"}
  ],
  "instructions": [
    "Pré-aqueça o forno a 180°C.",
    "Bata todos os ingredientes no liquidificador por 3 minutos.",
    "Despeje em forma untada e leve ao forno por 15 minutos.",
    "Deixe esfriar antes de desenformar."
  ],
  "tips": "Sirva com calda de chocolate ou sorvete. Conserva por 3 dias em geladeira.",
  "nutrition_estimate": {
    "calories": 280,
    "fat_g": 12,
    "carb_g": 38,
    "protein_g": 6
  },
  "image_prompt": "Foto 16:9 de bolo de chocolate fofinho cortado, textura úmida visível, luz natural suave, estilo food photography profissional",
  "social_short": {
    "tiktok_caption": "Bolo de 3 ingredientes que viralizou! 🍫✨ #receitafacil #tiktokfood #boloviral",
    "instagram_caption": "A receita mais fácil de bolo que você vai fazer! 🤎 #reels #receitas #bolodechocolate",
    "short_script": "1) Mostre o bolo pronto cortado; 2) Mostre os 3 ingredientes; 3) 'Tenta aí e me marca!'"
  },
  "publish_recommendation": {
    "publish": true,
    "priority": "viral"
  },
  "duplicate_fingerprint": "a7f2c9d...",
  "meta": {
    "seo_title": "Bolo de Chocolate 3 Ingredientes - Receita Viral TikTok",
    "meta_description": "Aprenda a fazer o bolo de chocolate viral do TikTok com apenas 3 ingredientes! Rápido, fácil e delicioso. 2.5M visualizações.",
    "duplicate": false
  },
  "audit": {
    "created_at": "2025-11-28T14:30:00Z",
    "processed_by": "viral-recipe-bot-v1",
    "confidence_score": 0.95,
    "notes": "Medidas convertidas de xícaras para gramas; vídeo original em inglês, legendas traduzidas"
  }
}
```

## 🔍 Fontes Monitoradas

### TikTok
- Hashtags: `#receita #food #tiktokfood #receitafacil #cozinha #comida`
- Trending sounds relacionados a culinária
- Perfis de culinária com alto engajamento

### Instagram
- Reels e posts no Explore/Feed
- Hashtags: `#reels #receitas #receitasfit #comidacaseira`
- Perfis de chefs e influenciadores

### RSS Feeds
- Agregadores de trends (configurável)
- Blogs culinários com RSS

## 🛡️ Regras Editoriais

- ✅ Atribuição obrigatória de fonte original
- ✅ Reescrita completa (não reprodução literal)
- ✅ Verificação de licenças de mídia
- ❌ Sem conteúdo protegido ou privado
- ❌ Sem instruções perigosas
- ❌ Sem plágio

## 📈 Métricas e Analytics

O sistema rastreia automaticamente:

- **Por receita**: views, cliques, tempo de leitura, compartilhamentos
- **Global**: taxa de conversão, engagement rate, receitas/hora
- **Ranking**: Atualizado a cada 15-60 minutos
- **Seção "Viral Agora"**: Top receitas em tempo real

## 🔧 Manutenção

```bash
# Ver status
python src/cli.py status

# Pausar monitoramento
python src/cli.py pause

# Retomar
python src/cli.py resume

# Limpar cache
python src/cli.py clear-cache

# Estatísticas
python src/cli.py stats
```

## 🐛 Troubleshooting

### Sistema não detecta receitas virais
- Verifique os thresholds em `.env`
- Confirme acesso às APIs/RSS feeds
- Veja logs em `logs/monitors.log`

### Receitas duplicadas sendo publicadas
- Ajuste `DUPLICATE_THRESHOLD` (padrão: 0.9)
- Verifique `logs/deduplication.log`

### Erros de scraping
- TikTok/Instagram podem bloquear IPs
- Use proxies rotativos (configurável)
- Habilite rate limiting

## 📄 Licença

MIT License - Veja LICENSE para detalhes

## 🤝 Contribuindo

Contribuições são bem-vindas! Abra uma issue ou PR.

---

**⚠️ Aviso Legal**: Este sistema deve respeitar os Termos de Serviço do TikTok e Instagram. Use responsavelmente e sempre atribua fontes originais.
