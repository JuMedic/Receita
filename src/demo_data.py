"""
Gerador de dados de demonstração para o sistema.
Cria receitas virais de exemplo para testar a interface.
"""
import random
from datetime import datetime, timedelta
from typing import List
from src.models import (
    Recipe, Source, Media, TrendMetrics, Ingredient, SocialShort,
    PublishRecommendation, Meta, Audit,
    SourceType, MediaType, MediaLicense, Category, Difficulty, Priority
)

# Receitas virais de exemplo
DEMO_RECIPES = [
    {
        "title": "Bolo de Chocolate de Caneca 2 Minutos",
        "category": Category.SOBREMESAS,
        "summary": "Bolo de chocolate super fofinho pronto em 2 minutos no microondas! Perfeito para matar a vontade de doce.",
        "ingredients": [
            {"name": "farinha de trigo", "quantity": "4", "unit": "colheres de sopa"},
            {"name": "açúcar", "quantity": "4", "unit": "colheres de sopa"},
            {"name": "chocolate em pó", "quantity": "2", "unit": "colheres de sopa"},
            {"name": "ovo", "quantity": "1", "unit": "unidade"},
            {"name": "leite", "quantity": "3", "unit": "colheres de sopa"},
            {"name": "óleo", "quantity": "3", "unit": "colheres de sopa"},
            {"name": "sal", "quantity": "1", "unit": "pitada"}
        ],
        "instructions": [
            "Misture todos os ingredientes secos na caneca",
            "Adicione o ovo, leite e óleo",
            "Misture bem com um garfo até ficar homogêneo",
            "Leve ao microondas por 2 minutos em potência máxima",
            "Espere esfriar um pouco e sirva"
        ],
        "prep_time": 2,
        "cook_time": 2,
        "serves": "1 pessoa",
        "difficulty": Difficulty.FACIL,
        "views": 2500000,
        "likes": 180000,
        "shares": 45000,
        "platform": SourceType.TIKTOK,
        "priority": Priority.VIRAL,
        "cost": "Baixo (R$ 5-10)"
    },
    {
        "title": "Pizza de Frigideira Sem Forno",
        "category": "massas",
        "summary": "Pizza deliciosa feita na frigideira! Sem precisar de forno, massa caseira super fácil e crocante.",
        "ingredients": [
            "1 xícara de farinha de trigo",
            "1/2 xícara de água morna",
            "1 colher de chá de fermento",
            "1 pitada de sal",
            "Molho de tomate",
            "Queijo mussarela",
            "Oregano a gosto"
        ],
        "instructions": [
            "Misture farinha, fermento, sal e água até formar uma massa",
            "Deixe descansar por 15 minutos",
            "Abra a massa e coloque na frigideira quente",
            "Quando dourar embaixo, vire e adicione molho e queijo",
            "Tampe a frigideira até o queijo derreter"
        ],
        "prep_time": 25,
        "serves": 2,
        "difficulty": "medium",
        "views": 1800000,
        "likes": 150000,
        "shares": 38000,
        "platform": "instagram",
        "priority": "viral"
    },
    {
        "title": "Mousse de Maracujá 3 Ingredientes",
        "category": "sobremesas",
        "summary": "Mousse cremoso de maracujá com apenas 3 ingredientes! Super fácil e rende muito.",
        "ingredients": [
            "1 lata de leite condensado",
            "1 lata de creme de leite",
            "1 xícara de suco de maracujá concentrado"
        ],
        "instructions": [
            "Bata no liquidificador o leite condensado e o suco de maracujá",
            "Adicione o creme de leite e bata rapidamente",
            "Distribua em tacinhas",
            "Leve à geladeira por 2 horas",
            "Decore com sementes de maracujá"
        ],
        "prep_time": 10,
        "serves": 6,
        "difficulty": "easy",
        "views": 950000,
        "likes": 85000,
        "shares": 22000,
        "platform": "tiktok",
        "priority": "highlight"
    },
    {
        "title": "Pão de Queijo de Liquidificador",
        "category": "paes",
        "summary": "Pão de queijo super fácil! Tudo no liquidificador, sem sujar as mãos. Fica crocante por fora e macio por dentro.",
        "ingredients": [
            "1 xícara de leite",
            "1/2 xícara de óleo",
            "2 ovos",
            "1 pitada de sal",
            "2 xícaras de polvilho azedo",
            "1 xícara de queijo ralado"
        ],
        "instructions": [
            "Bata no liquidificador leite, óleo, ovos e sal",
            "Transfira para uma tigela",
            "Adicione o polvilho aos poucos mexendo",
            "Adicione o queijo e misture",
            "Unte uma forma e despeje a massa",
            "Asse a 180°C por 40 minutos"
        ],
        "prep_time": 50,
        "serves": 8,
        "difficulty": "easy",
        "views": 1200000,
        "likes": 98000,
        "shares": 28000,
        "platform": "instagram",
        "priority": "highlight"
    },
    {
        "title": "Brigadeiro de Colher Fit",
        "category": "sobremesas",
        "summary": "Brigadeiro cremoso fit com apenas 100 calorias! Sem leite condensado, perfeito para dieta.",
        "ingredients": [
            "1 xícara de leite desnatado",
            "3 colheres de cacau em pó 100%",
            "2 colheres de adoçante culinário",
            "1 colher de amido de milho",
            "1 pitada de sal"
        ],
        "instructions": [
            "Misture todos os ingredientes numa panela",
            "Leve ao fogo médio mexendo sempre",
            "Cozinhe até engrossar e soltar do fundo",
            "Transfira para um pote",
            "Deixe esfriar e leve à geladeira"
        ],
        "prep_time": 15,
        "serves": 4,
        "difficulty": "easy",
        "views": 780000,
        "likes": 65000,
        "shares": 15000,
        "platform": "tiktok",
        "priority": "normal"
    },
    {
        "title": "Sanduíche Natural de Frango",
        "category": "lanches",
        "summary": "Sanduíche natural super recheado e saudável! Perfeito para levar pro trabalho ou faculdade.",
        "ingredients": [
            "1 peito de frango desfiado",
            "2 colheres de cream cheese light",
            "1 cenoura ralada",
            "Alface e tomate",
            "Pão integral",
            "Sal e pimenta a gosto"
        ],
        "instructions": [
            "Tempere e cozinhe o frango",
            "Desfie o frango e misture com cream cheese",
            "Adicione a cenoura ralada",
            "Tempere com sal e pimenta",
            "Monte o sanduíche com alface e tomate"
        ],
        "prep_time": 30,
        "serves": 2,
        "difficulty": "easy",
        "views": 620000,
        "likes": 48000,
        "shares": 12000,
        "platform": "instagram",
        "priority": "normal"
    },
    {
        "title": "Panqueca Americana Fofa",
        "category": "cafedamanha",
        "summary": "Panqueca americana super alta e fofinha! Segredo para ficar perfeita toda vez.",
        "ingredients": [
            "1 xícara de farinha de trigo",
            "1 colher de sopa de açúcar",
            "1 colher de chá de fermento",
            "1 pitada de sal",
            "1 xícara de leite",
            "1 ovo",
            "2 colheres de manteiga derretida"
        ],
        "instructions": [
            "Misture os ingredientes secos numa tigela",
            "Em outra tigela, bata o ovo, leite e manteiga",
            "Junte os líquidos aos secos e misture levemente",
            "Aqueça uma frigideira antiaderente",
            "Despeje porções da massa e cozinhe até aparecer bolhas",
            "Vire e doure o outro lado"
        ],
        "prep_time": 20,
        "serves": 3,
        "difficulty": "medium",
        "views": 1400000,
        "likes": 125000,
        "shares": 32000,
        "platform": "tiktok",
        "priority": "viral"
    },
    {
        "title": "Brownie de Microondas Pronto em 3min",
        "category": "sobremesas",
        "summary": "Brownie super cremoso e chocolatudo pronto em 3 minutos! Impossível resistir.",
        "ingredients": [
            "3 colheres de sopa de farinha",
            "3 colheres de sopa de açúcar",
            "2 colheres de sopa de chocolate em pó",
            "2 colheres de sopa de óleo",
            "3 colheres de sopa de leite",
            "1 ovo",
            "Gotas de chocolate"
        ],
        "instructions": [
            "Misture tudo numa tigela pequena",
            "Adicione gotas de chocolate",
            "Despeje numa caneca grande",
            "Microondas por 3 minutos",
            "Sirva quente com sorvete"
        ],
        "prep_time": 5,
        "serves": 1,
        "difficulty": "easy",
        "views": 3200000,
        "likes": 245000,
        "shares": 58000,
        "platform": "tiktok",
        "priority": "viral"
    }
]


def generate_demo_recipes(count: int = None) -> List[Recipe]:
    """
    Gera receitas de demonstração.
    
    Args:
        count: Número de receitas (None = todas)
    
    Returns:
        Lista de objetos Recipe
    """
    recipes_to_use = DEMO_RECIPES if count is None else DEMO_RECIPES[:count]
    
    demo_recipes = []
    for idx, recipe_data in enumerate(recipes_to_use):
        # Criar timestamps realistas
        hours_ago = random.randint(1, 72)
        detected_at = datetime.utcnow() - timedelta(hours=hours_ago)
        
        recipe = Recipe(
            title=recipe_data["title"],
            slug=f"demo-recipe-{idx+1}",
            summary=recipe_data["summary"],
            category=recipe_data["category"],
            ingredients=recipe_data["ingredients"],
            instructions=recipe_data["instructions"],
            prep_time_minutes=recipe_data["prep_time"],
            servings=recipe_data["serves"],
            difficulty=recipe_data["difficulty"],
            source_platform=recipe_data["platform"],
            source_url=f"https://{recipe_data['platform']}.com/@demo/video/{random.randint(1000000, 9999999)}",
            author_name=f"@chef{random.choice(['master', 'pro', 'top', 'viral', 'best'])}{random.randint(100, 999)}",
            author_followers=random.randint(50000, 5000000),
            media_url=f"https://cdn.example.com/demo/{idx+1}.jpg",
            thumbnail_url=f"https://cdn.example.com/demo/{idx+1}_thumb.jpg",
            views=recipe_data["views"],
            likes=recipe_data["likes"],
            shares=recipe_data["shares"],
            comments=random.randint(500, 50000),
            engagement_rate=round((recipe_data["likes"] / recipe_data["views"]) * 100, 2),
            viral_score=round(random.uniform(75, 99), 1),
            priority=recipe_data["priority"],
            tags=[recipe_data["category"], "viral", "fácil", "rápido"],
            detected_at=detected_at,
            processed_at=datetime.utcnow()
        )
        demo_recipes.append(recipe)
    
    return demo_recipes


def generate_demo_signals(count: int = 20) -> List[ViralSignal]:
    """
    Gera sinais virais de demonstração.
    
    Args:
        count: Número de sinais a gerar
    
    Returns:
        Lista de ViralSignal
    """
    recipes = generate_demo_recipes()
    signals = []
    
    for idx, recipe in enumerate(recipes[:count]):
        signal = ViralSignal(
            platform=recipe.source_platform,
            content_id=f"demo_{recipe.source_platform}_{idx}",
            url=recipe.source_url,
            title=recipe.title,
            author=recipe.author_name,
            views=recipe.views,
            likes=recipe.likes,
            shares=recipe.shares,
            comments=recipe.comments,
            detected_at=recipe.detected_at,
            viral_score=recipe.viral_score
        )
        signals.append(signal)
    
    return signals
