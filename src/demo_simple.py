"""
Gerador simplificado de receitas demo
"""
import hashlib
from datetime import datetime
from src.models import *

def create_demo_recipe(idx: int, title: str, category: Category, views: int, likes: int, 
                       shares: int, platform: SourceType, priority: Priority) -> Recipe:
    """Cria uma receita demo com todos os campos obrigatórios"""
    
    slug = title.lower().replace(" ", "-")[:50]
    author = f"@chef{idx}"
    url = f"https://{platform.value}.com/{author}/video/{1000000 + idx}"
    
    return Recipe(
        title=title,
        slug=slug,
        summary=f"{title[:80]}...",
        
        source=Source(
            type=platform,
            profile=author,
            name=f"Chef Demo {idx}",
            url=url
        ),
        
        media=Media(
            media_type=MediaType.VIDEO,
            media_url=f"https://cdn.example.com/demo{idx}.mp4",
            thumbnail_frame_time="5s",
            media_license=MediaLicense.PUBLIC
        ),
        
        trend_metrics=TrendMetrics(
            views=views,
            likes=likes,
            shares=shares,
            growth_rate_percent=75.0,
            time_window_hours=24
        ),
        
        category=category,
        tags=["viral", "fácil", category.value.lower()],
        
        servings="2 porções",
        prep_time_minutes=10,
        cook_time_minutes=15,
        total_time_minutes=25,
        difficulty=Difficulty.FACIL,
        estimated_cost="Baixo (R$ 10-20)",
        
        ingredients=[
            Ingredient(name="Ingrediente 1", quantity="200", unit="g"),
            Ingredient(name="Ingrediente 2", quantity="1", unit="xícara"),
        ],
        
        instructions=[
            "Passo 1: Prepare os ingredientes",
            "Passo 2: Misture tudo",
            "Passo 3: Cozinhe por 15 minutos"
        ],
        
        social_short=SocialShort(
            tiktok_caption=f"🔥 {title}! #receita #viral",
            instagram_caption=f"✨ {title}!\n\nVeja o passo a passo completo! 👆",
            short_script="1. Prepare 2. Misture 3. Sirva!"
        ),
        
        publish_recommendation=PublishRecommendation(
            publish=True,
            priority=priority
        ),
        
        duplicate_fingerprint=hashlib.sha256(title.encode()).hexdigest()[:16],
        
        meta=Meta(
            seo_title=title[:60],
            meta_description=f"Aprenda a fazer {title}"[:150],
            duplicate=False
        ),
        
        audit=Audit(
            created_at=datetime.utcnow(),
            processed_by="demo_generator",
            confidence_score=0.95
        )
    )


def generate_demo_recipes() -> list[Recipe]:
    """Gera 8 receitas demo"""
    
    recipes_data = [
        ("Bolo de Chocolate de Caneca 2min", Category.SOBREMESAS, 2500000, 180000, 45000, SourceType.TIKTOK, Priority.VIRAL),
        ("Pizza de Frigideira Sem Forno", Category.MASSAS, 1800000, 150000, 38000, SourceType.INSTAGRAM, Priority.VIRAL),
        ("Mousse de Maracujá 3 Ingredientes", Category.SOBREMESAS, 950000, 85000, 22000, SourceType.TIKTOK, Priority.HIGHLIGHT),
        ("Pão de Queijo de Liquidificador", Category.SOBREMESAS, 1200000, 98000, 28000, SourceType.INSTAGRAM, Priority.HIGHLIGHT),
        ("Brigadeiro de Colher Fit", Category.SOBREMESAS, 780000, 65000, 15000, SourceType.TIKTOK, Priority.NORMAL),
        ("Sanduíche Natural de Frango", Category.SALGADOS, 620000, 48000, 12000, SourceType.INSTAGRAM, Priority.NORMAL),
        ("Panqueca Americana Fofa", Category.CAFE_DA_MANHA, 1400000, 125000, 32000, SourceType.TIKTOK, Priority.VIRAL),
        ("Brownie de Microondas 3min", Category.DOCES, 3200000, 245000, 58000, SourceType.TIKTOK, Priority.VIRAL),
    ]
    
    return [create_demo_recipe(i+1, *data) for i, data in enumerate(recipes_data)]
