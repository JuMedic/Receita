"""
Modelos de dados do sistema de receitas virais.
Define estruturas Pydantic para validação e serialização.
"""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum


class SourceType(str, Enum):
    """Tipos de fonte de conteúdo"""
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    RSS = "rss"
    USER_UPLOAD = "user_upload"
    GENERATED = "generated"


class MediaType(str, Enum):
    """Tipos de mídia"""
    VIDEO = "video"
    IMAGE = "image"


class MediaLicense(str, Enum):
    """Tipos de licença de mídia"""
    PUBLIC = "public"
    UNKNOWN = "unknown"
    RESTRICTED = "restricted"


class Difficulty(str, Enum):
    """Níveis de dificuldade"""
    FACIL = "Fácil"
    MEDIO = "Médio"
    DIFICIL = "Difícil"


class Category(str, Enum):
    """Categorias de receitas"""
    RAPIDAS = "Rápidas"
    DOCES = "Doces"
    SALGADOS = "Salgados"
    BEBIDAS = "Bebidas"
    VEGANA = "Vegana"
    FITNESS = "Fitness"
    MASSAS = "Massas"
    CARNES = "Carnes"
    SOBREMESAS = "Sobremesas"
    CAFE_DA_MANHA = "Café da Manhã"


class Priority(str, Enum):
    """Prioridades de publicação"""
    NORMAL = "normal"
    HIGHLIGHT = "highlight"
    VIRAL = "viral"


class Source(BaseModel):
    """Informações da fonte do conteúdo"""
    type: SourceType
    profile: str = Field(..., description="Nome do perfil/usuário")
    name: str = Field(..., description="Nome completo do perfil/site")
    url: HttpUrl = Field(..., description="URL do post original")


class Media(BaseModel):
    """Informações de mídia"""
    media_type: MediaType
    media_url: HttpUrl = Field(..., description="URL do vídeo ou imagem")
    thumbnail_frame_time: Optional[str] = Field(None, description="Tempo do frame para thumbnail (ex: '12s')")
    media_license: MediaLicense = MediaLicense.UNKNOWN


class TrendMetrics(BaseModel):
    """Métricas de viralização"""
    views: int = Field(..., ge=0)
    likes: int = Field(..., ge=0)
    shares: int = Field(..., ge=0)
    growth_rate_percent: float = Field(..., ge=0, description="Taxa de crescimento percentual")
    time_window_hours: int = Field(..., ge=1, le=168, description="Janela temporal da análise")
    
    @validator('growth_rate_percent')
    def validate_growth_rate(cls, v):
        if v > 10000:  # Limitar crescimento absurdo
            raise ValueError('Growth rate excessivamente alto, possível erro')
        return v


class Ingredient(BaseModel):
    """Ingrediente da receita"""
    name: str = Field(..., min_length=1)
    quantity: str = Field(..., description="Quantidade (número ou texto)")
    unit: str = Field(..., description="Unidade de medida")


class NutritionEstimate(BaseModel):
    """Estimativa nutricional"""
    calories: Optional[int] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)
    carb_g: Optional[float] = Field(None, ge=0)
    protein_g: Optional[float] = Field(None, ge=0)


class SocialShort(BaseModel):
    """Conteúdo para redes sociais"""
    tiktok_caption: str = Field(..., max_length=300)
    instagram_caption: str = Field(..., max_length=2200)
    short_script: str = Field(..., description="Script de 3 passos para Shorts/Reels")


class PublishRecommendation(BaseModel):
    """Recomendação de publicação"""
    publish: bool = Field(..., description="Se deve ser publicado automaticamente")
    priority: Priority = Priority.NORMAL


class Meta(BaseModel):
    """Metadados SEO"""
    seo_title: str = Field(..., max_length=60)
    meta_description: str = Field(..., max_length=150)
    duplicate: bool = False
    normalization_issues: Optional[str] = None


class Audit(BaseModel):
    """Auditoria e rastreamento"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_by: str = Field(..., description="ID do sistema/modelo que processou")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    notes: Optional[str] = Field(None, description="Observações sobre o processamento")


class Recipe(BaseModel):
    """Modelo completo de receita viral"""
    title: str = Field(..., min_length=5, max_length=120)
    slug: str = Field(..., min_length=5, max_length=150)
    summary: str = Field(..., max_length=150)
    
    source: Source
    media: Media
    trend_metrics: TrendMetrics
    
    category: Category
    tags: List[str] = Field(..., min_items=1, max_items=20)
    
    servings: str = Field(..., description="Número de porções")
    prep_time_minutes: int = Field(..., ge=0, le=1440)
    cook_time_minutes: int = Field(..., ge=0, le=1440)
    total_time_minutes: int = Field(..., ge=0, le=1440)
    difficulty: Difficulty
    estimated_cost: str = Field(..., description="Faixa de custo estimado")
    
    ingredients: List[Ingredient] = Field(..., min_items=2)
    instructions: List[str] = Field(..., min_items=2)
    tips: Optional[str] = None
    
    nutrition_estimate: Optional[NutritionEstimate] = None
    image_prompt: Optional[str] = Field(None, description="Prompt para geração de imagem por IA")
    
    social_short: SocialShort
    publish_recommendation: PublishRecommendation
    
    duplicate_fingerprint: str = Field(..., description="Hash para deduplicação")
    meta: Meta
    audit: Audit
    
    @validator('total_time_minutes')
    def validate_total_time(cls, v, values):
        if 'prep_time_minutes' in values and 'cook_time_minutes' in values:
            expected = values['prep_time_minutes'] + values['cook_time_minutes']
            if abs(v - expected) > 5:  # Tolerância de 5 minutos
                raise ValueError('Total time deve ser aproximadamente prep + cook time')
        return v
    
    @validator('slug')
    def validate_slug(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug deve conter apenas letras, números, hífens e underscores')
        return v.lower()


class RecipeError(BaseModel):
    """Modelo de erro no processamento"""
    error: str = Field(..., description="Tipo de erro")
    missing: Optional[List[str]] = Field(None, description="Campos faltantes")
    message: Optional[str] = Field(None, description="Mensagem de erro detalhada")


class RawSocialContent(BaseModel):
    """Conteúdo bruto capturado das redes sociais"""
    source_type: SourceType
    source_url: str
    source_profile: str
    raw_title: Optional[str] = None
    raw_caption: Optional[str] = None
    media_url: Optional[str] = None
    published_at: datetime
    
    # Métricas brutas
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    
    # Metadados
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    sound_id: Optional[str] = None
    sound_name: Optional[str] = None
    
    captured_at: datetime = Field(default_factory=datetime.utcnow)


class ViralSignal(BaseModel):
    """Sinal de viralização detectado"""
    content: RawSocialContent
    is_viral: bool
    viral_score: float = Field(..., ge=0.0, le=1.0)
    growth_rate: float
    time_window_hours: int
    signals_detected: List[str] = Field(
        default_factory=list,
        description="Lista de sinais que confirmam viralização"
    )
    reason: Optional[str] = None
