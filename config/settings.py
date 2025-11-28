"""
Configurações centralizadas do sistema de receitas virais.
Carrega variáveis de ambiente e fornece valores padrão.
"""
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
MEDIA_DIR = DATA_DIR / "media"
CACHE_DIR = DATA_DIR / "cache"

# Criar diretórios se não existirem
for directory in [DATA_DIR, LOGS_DIR, MEDIA_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class Config:
    """Configurações globais do sistema"""
    
    # ====== MODO DE OPERAÇÃO ======
    AUTO_MODE: bool = os.getenv("AUTO_MODE", "true").lower() == "true"
    CYCLE_MINUTES: int = int(os.getenv("CYCLE_MINUTES", "10"))
    ENABLE_SCHEDULER: bool = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
    
    # ====== THRESHOLDS DE VIRALIZAÇÃO ======
    THRESHOLD_VIRAL_VIEWS: int = int(os.getenv("THRESHOLD_VIRAL_VIEWS", "100000"))
    THRESHOLD_VIRAL_LIKES: int = int(os.getenv("THRESHOLD_VIRAL_LIKES", "5000"))
    THRESHOLD_VIRAL_SHARES: int = int(os.getenv("THRESHOLD_VIRAL_SHARES", "500"))
    THRESHOLD_GROWTH_RATE: float = float(os.getenv("THRESHOLD_GROWTH_RATE", "50"))
    TIME_WINDOW_HOURS: int = int(os.getenv("TIME_WINDOW_HOURS", "6"))
    
    # ====== FILTROS DE RECEITA ======
    MAX_INGREDIENTS_VIRAL: int = int(os.getenv("MAX_INGREDIENTS_VIRAL", "10"))
    MAX_PREP_MINUTES_VIRAL: int = int(os.getenv("MAX_PREP_MINUTES_VIRAL", "30"))
    MIN_INGREDIENTS: int = int(os.getenv("MIN_INGREDIENTS", "2"))
    MIN_INSTRUCTIONS: int = int(os.getenv("MIN_INSTRUCTIONS", "2"))
    
    # ====== DEDUPLICAÇÃO ======
    DUPLICATE_THRESHOLD: float = float(os.getenv("DUPLICATE_THRESHOLD", "0.9"))
    ENABLE_FUZZY_MATCHING: bool = os.getenv("ENABLE_FUZZY_MATCHING", "true").lower() == "true"
    
    # ====== APIs EXTERNAS ======
    TIKTOK_API_KEY: str = os.getenv("TIKTOK_API_KEY", "")
    TIKTOK_API_SECRET: str = os.getenv("TIKTOK_API_SECRET", "")
    INSTAGRAM_GRAPH_API_TOKEN: str = os.getenv("INSTAGRAM_GRAPH_API_TOKEN", "")
    INSTAGRAM_APP_ID: str = os.getenv("INSTAGRAM_APP_ID", "")
    INSTAGRAM_APP_SECRET: str = os.getenv("INSTAGRAM_APP_SECRET", "")
    
    # ====== RSS FEEDS ======
    RSS_FEED_URLS: List[str] = os.getenv("RSS_FEED_URLS", "").split(",") if os.getenv("RSS_FEED_URLS") else []
    RSS_CHECK_INTERVAL_MINUTES: int = int(os.getenv("RSS_CHECK_INTERVAL_MINUTES", "15"))
    
    # ====== SCRAPING ======
    ENABLE_SCRAPING: bool = os.getenv("ENABLE_SCRAPING", "true").lower() == "true"
    USE_PROXIES: bool = os.getenv("USE_PROXIES", "false").lower() == "true"
    PROXY_LIST: List[str] = os.getenv("PROXY_LIST", "").split(",") if os.getenv("PROXY_LIST") else []
    USER_AGENT: str = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    REQUEST_DELAY_SECONDS: int = int(os.getenv("REQUEST_DELAY_SECONDS", "2"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # ====== MÍDIA ======
    MEDIA_DOWNLOAD_ENABLED: bool = os.getenv("MEDIA_DOWNLOAD_ENABLED", "true").lower() == "true"
    THUMBNAIL_GENERATION: bool = os.getenv("THUMBNAIL_GENERATION", "true").lower() == "true"
    THUMBNAIL_FRAME_TIME: int = int(os.getenv("THUMBNAIL_FRAME_TIME", "8"))
    MEDIA_STORAGE_PATH: Path = Path(os.getenv("MEDIA_STORAGE_PATH", str(MEDIA_DIR)))
    MAX_MEDIA_SIZE_MB: int = int(os.getenv("MAX_MEDIA_SIZE_MB", "50"))
    
    # ====== DATABASE ======
    DATABASE_PATH: Path = Path(os.getenv("DATABASE_PATH", str(DATA_DIR / "recipes.db")))
    CACHE_PATH: Path = Path(os.getenv("CACHE_PATH", str(CACHE_DIR)))
    ENABLE_DATABASE_BACKUP: bool = os.getenv("ENABLE_DATABASE_BACKUP", "true").lower() == "true"
    BACKUP_INTERVAL_HOURS: int = int(os.getenv("BACKUP_INTERVAL_HOURS", "24"))
    
    # ====== PUBLICAÇÃO ======
    CMS_ENDPOINT: str = os.getenv("CMS_ENDPOINT", "http://localhost:8000/api/recipes")
    CMS_API_KEY: str = os.getenv("CMS_API_KEY", "")
    PUBLISH_BATCH_SIZE: int = int(os.getenv("PUBLISH_BATCH_SIZE", "5"))
    RETRY_FAILED_PUBLISHES: bool = os.getenv("RETRY_FAILED_PUBLISHES", "true").lower() == "true"
    
    # ====== ANALYTICS ======
    ENABLE_ANALYTICS: bool = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
    METRICS_UPDATE_INTERVAL_MINUTES: int = int(os.getenv("METRICS_UPDATE_INTERVAL_MINUTES", "30"))
    VIRAL_RANKING_TOP_N: int = int(os.getenv("VIRAL_RANKING_TOP_N", "20"))
    TRACK_USER_ENGAGEMENT: bool = os.getenv("TRACK_USER_ENGAGEMENT", "true").lower() == "true"
    
    # ====== NOTIFICAÇÕES ======
    ENABLE_NOTIFICATIONS: bool = os.getenv("ENABLE_NOTIFICATIONS", "false").lower() == "true"
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
    DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")
    
    # ====== LOGGING ======
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_PATH: Path = Path(os.getenv("LOG_PATH", str(LOGS_DIR)))
    LOG_MAX_SIZE_MB: int = int(os.getenv("LOG_MAX_SIZE_MB", "100"))
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "10"))
    
    # ====== API SERVER ======
    ENABLE_API_SERVER: bool = os.getenv("ENABLE_API_SERVER", "true").lower() == "true"
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8080"))
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "change-this-secret-key-in-production")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    # ====== SEGURANÇA ======
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW_MINUTES: int = int(os.getenv("RATE_LIMIT_WINDOW_MINUTES", "15"))
    
    # ====== PERFORMANCE ======
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    
    # ====== HASHTAGS E KEYWORDS ======
    TIKTOK_HASHTAGS: List[str] = os.getenv("TIKTOK_HASHTAGS", "receita,food,tiktokfood,receitafacil").split(",")
    INSTAGRAM_HASHTAGS: List[str] = os.getenv("INSTAGRAM_HASHTAGS", "reels,receitas,receitasfit").split(",")
    YOUTUBE_KEYWORDS: List[str] = os.getenv("YOUTUBE_KEYWORDS", "shorts,receita,comida").split(",")
    
    # ====== LOCALIZAÇÃO ======
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "pt-BR")
    CURRENCY: str = os.getenv("CURRENCY", "BRL")
    TIMEZONE: str = os.getenv("TIMEZONE", "America/Sao_Paulo")
    
    # ====== DESENVOLVIMENTO ======
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    ENABLE_PROFILING: bool = os.getenv("ENABLE_PROFILING", "false").lower() == "true"
    MOCK_EXTERNAL_APIS: bool = os.getenv("MOCK_EXTERNAL_APIS", "false").lower() == "true"


# Instância global de configuração
config = Config()
