# 🏗️ Arquitetura do Sistema

## Visão Geral

O sistema opera em **ciclos contínuos** (configurável: 5-10 minutos), executando uma pipeline completa de detecção → processamento → publicação de receitas virais.

```
┌────────────────────────────────────────────────────────────────┐
│                    SYSTEM ORCHESTRATOR                         │
│                   (Loop Principal 24/7)                        │
└────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │   TikTok     │ │  Instagram   │ │     RSS      │
      │   Monitor    │ │   Monitor    │ │   Monitor    │
      └──────────────┘ └──────────────┘ └──────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                    ViralSignals (multi-signal)
                              │
                              ▼
                    ┌──────────────────┐
                    │     Recipe       │
                    │    Processor     │
                    │  (Rewrite + AI)  │
                    └──────────────────┘
                              │
                    Structured Recipes
                              │
                              ▼
                    ┌──────────────────┐
                    │  Deduplication   │
                    │    Service       │
                    │  (Fingerprint)   │
                    └──────────────────┘
                              │
                    Unique Recipes
                              │
                              ▼
                    ┌──────────────────┐
                    │   Publisher      │
                    │    Service       │
                    │ (Auto/Manual)    │
                    └──────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌─────────────┐     ┌─────────────┐
            │     CMS     │     │    Admin    │
            │ (Auto Mode) │     │   Review    │
            └─────────────┘     └─────────────┘
```

---

## Componentes Principais

### 1. System Orchestrator
**Arquivo:** `src/orchestrator/system_orchestrator.py`

**Responsabilidades:**
- Loop principal 24/7
- Coordenação de todos os módulos
- Gestão de ciclos temporizados
- Logging e estatísticas globais
- Shutdown gracioso

**Ciclo de Execução:**
```python
while is_running:
    1. Monitoramento (todos os monitores em paralelo)
    2. Processamento (cada sinal viral → receita)
    3. Deduplicação (fingerprint + similaridade)
    4. Publicação (auto ou manual)
    5. Sleep(CYCLE_MINUTES)
```

---

### 2. Monitores (Monitor Coordinator)
**Arquivos:** `src/monitors/*.py`

#### TikTokMonitor
- **API:** TikTok Official API (se disponível)
- **Scraping:** Playwright/Selenium para trending
- **Hashtags:** Configuráveis via `TIKTOK_HASHTAGS`
- **Metrics:** views, likes, shares, comments, sound_id

#### InstagramMonitor
- **API:** Instagram Graph API (Business accounts)
- **Scraping:** Limitado (requer auth)
- **Focus:** Reels, Explore, Feed
- **Metrics:** impressions, likes, shares, comments

#### RSSMonitor
- **Feeds:** URLs configuráveis via `RSS_FEED_URLS`
- **Parser:** feedparser
- **Filter:** Apenas conteúdo relacionado a receitas

**Detecção de Viralização:**
```python
def is_viral(content):
    signals = []
    
    if views >= THRESHOLD_VIRAL_VIEWS:
        signals.append("high_views")
    
    if likes >= THRESHOLD_VIRAL_LIKES:
        signals.append("high_likes")
    
    if shares >= THRESHOLD_VIRAL_SHARES:
        signals.append("high_shares")
    
    if growth_rate >= THRESHOLD_GROWTH_RATE:
        signals.append("high_growth")
    
    # Precisa de pelo menos 2 sinais fortes
    return len(signals) >= 2
```

---

### 3. Recipe Processor
**Arquivo:** `src/processors/recipe_processor.py`

**Pipeline de Processamento:**

```
Raw Content (TikTok/Instagram/RSS)
         │
         ▼
┌──────────────────┐
│   Extraction     │ ← NLP/Regex/LLM
│ - Title          │
│ - Ingredients    │
│ - Instructions   │
│ - Time, Servings │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│   Rewriting      │ ← LLM (GPT-4/Claude)
│ - SEO Title      │
│ - Summary        │
│ - Original Text  │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  Normalization   │
│ - Ingredients    │
│   (xícara → g)   │
│ - Units          │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  Enrichment      │
│ - Nutrition      │
│ - Cost Estimate  │
│ - Category       │
│ - Social Content │
│ - Image Prompt   │
└──────────────────┘
         │
         ▼
   Structured Recipe
```

**LLM Integration (Futuro):**
- Usar OpenAI/Claude para reescrita profissional
- Extração inteligente de ingredientes
- Geração de variações (vegana, sem glúten, etc)
- Estimativas nutricionais precisas

---

### 4. Deduplication Service
**Arquivo:** `src/utils/deduplication.py`

**Estratégias:**

1. **Fingerprint Exato:**
   ```python
   hash(normalized_title + sorted_ingredients)
   ```

2. **Similaridade de Título:**
   - Jaccard similarity com n-grams
   - Threshold: 0.9 (configurável)

3. **Similaridade de Ingredientes:**
   - Set intersection/union
   - Threshold: 0.9

**Decisão:**
```python
if fingerprint_match:
    return DUPLICATE

if title_similarity > 0.9 AND ingredient_similarity > 0.9:
    return DUPLICATE

return UNIQUE
```

---

### 5. Publisher Service
**Arquivo:** `src/publishers/publisher_service.py`

**Modos de Operação:**

#### Modo Automático (`AUTO_MODE=true`)
```python
if recipe.publish_recommendation.publish:
    publish_to_cms(recipe)
else:
    send_to_admin_review(recipe)
```

#### Modo Manual (`AUTO_MODE=false`)
```python
# Todas as receitas vão para revisão
pending_approval.append(recipe)
```

**CMS Integration:**
- REST API endpoint configurável
- JSON payload com receita completa
- Retry logic para falhas
- Batch processing

---

## Fluxo de Dados

### Input (Raw Content)
```python
RawSocialContent:
    - source_url
    - raw_title
    - raw_caption
    - media_url
    - views, likes, shares
    - hashtags, mentions
    - published_at
```

### Processing (Viral Signal)
```python
ViralSignal:
    - content: RawSocialContent
    - is_viral: bool
    - viral_score: 0.0-1.0
    - growth_rate: float
    - signals_detected: List[str]
```

### Output (Structured Recipe)
```python
Recipe:
    - title, slug, summary
    - source (type, profile, url)
    - media (video/image + thumbnail)
    - trend_metrics (views, likes, shares, growth)
    - ingredients[] (name, quantity, unit)
    - instructions[] (step-by-step)
    - nutrition_estimate
    - social_short (captions + script)
    - publish_recommendation
    - duplicate_fingerprint
    - meta (SEO)
    - audit (tracking)
```

---

## Escalabilidade

### Horizontal Scaling
- Múltiplas instâncias do sistema
- Load balancer para distribuir requests
- Redis para cache compartilhado
- PostgreSQL para dados centralizados

### Vertical Scaling
- Aumentar `MAX_WORKERS` para mais threads
- Mais RAM para cache maior
- SSD para I/O rápido

### Performance Otimizations
- Async/await para I/O não-bloqueante
- Batch processing (publicação)
- Cache de fingerprints
- Lazy loading de media

---

## Segurança & Compliance

### Rate Limiting
- Por plataforma (TikTok, Instagram)
- Por endpoint de API
- Exponential backoff em falhas

### Data Privacy
- Não armazena dados pessoais
- Apenas URLs públicas
- Atribuição obrigatória de fonte

### Legal
- Respeita Terms of Service
- Reescrita para evitar plágio
- Licenças de mídia verificadas

---

## Monitoramento & Observabilidade

### Logs
```
logs/
├── app.log           # Log geral
├── errors.log        # Apenas erros
├── monitors.log      # Atividade dos monitores
├── processors.log    # Processamento
└── publishers.log    # Publicação
```

### Métricas
- Total de ciclos executados
- Receitas processadas
- Taxa de duplicação
- Taxa de publicação
- Uptime do sistema

### Alertas (Futuro)
- Slack/Discord webhooks
- Email notifications
- Prometheus + Grafana

---

## Tecnologias Utilizadas

### Core
- **Python 3.11+**
- **AsyncIO** - Operações assíncronas
- **Pydantic** - Validação de dados

### Web & APIs
- **aiohttp** - HTTP async client
- **FastAPI** - API server (futuro)
- **feedparser** - RSS parsing

### Scraping
- **BeautifulSoup** - HTML parsing
- **Selenium/Playwright** - Browser automation
- **lxml** - XML/HTML parsing

### Data
- **SQLAlchemy** - ORM
- **Redis** - Cache (opcional)
- **PostgreSQL** - Database (opcional)

### AI/ML (Futuro)
- **OpenAI API** - GPT-4 para reescrita
- **Anthropic Claude** - Processamento de texto
- **Transformers** - NLP local

### DevOps
- **Docker** - Containerização
- **docker-compose** - Orquestração
- **loguru** - Logging avançado

---

## Roadmap Futuro

### v1.1 - Analytics Dashboard
- UI web para visualizar métricas
- Gráficos de tendências
- Top receitas virais

### v1.2 - LLM Integration
- OpenAI/Claude para reescrita profissional
- Geração de variações de receitas
- Estimativas nutricionais precisas

### v1.3 - Media Processing
- Download e hosting de vídeos/imagens
- Geração automática de thumbnails
- Conversão de formatos

### v1.4 - Advanced Features
- Webhook notifications
- Scheduler avançado (horários específicos)
- A/B testing de títulos
- SEO scoring automático

---

## Contribuindo

Veja `CONTRIBUTING.md` para guidelines de desenvolvimento.

## Licença

MIT License - Veja `LICENSE` para detalhes.
