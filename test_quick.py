"""
Teste rápido do sistema - executa um ciclo de demonstração.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import config
from src.utils.logger import app_logger
from src.monitors import MonitorCoordinator
from src.processors.recipe_processor import RecipeProcessor
from src.utils.deduplication import DeduplicationService
from src.publishers.publisher_service import PublisherService


async def test_system():
    """Testa sistema com um ciclo completo"""
    
    print("=" * 70)
    print("🧪 TESTE RÁPIDO DO SISTEMA DE RECEITAS VIRAIS")
    print("=" * 70)
    print()
    
    # Forçar modo mock
    config.MOCK_EXTERNAL_APIS = True
    
    print("📋 Configuração:")
    print(f"  • Modo Mock: {config.MOCK_EXTERNAL_APIS}")
    print(f"  • Auto Mode: {config.AUTO_MODE}")
    print(f"  • Threshold Views: {config.THRESHOLD_VIRAL_VIEWS}")
    print()
    
    # 1. MONITORAMENTO
    print("🔍 FASE 1: Monitoramento")
    print("-" * 70)
    
    monitor_coord = MonitorCoordinator()
    viral_signals = await monitor_coord.run_all_monitors()
    
    print(f"✓ Detectados: {len(viral_signals)} sinais virais")
    print()
    
    if not viral_signals:
        print("⚠️  Nenhum sinal viral detectado. Ajuste os thresholds.")
        return
    
    # Mostrar alguns exemplos
    for i, signal in enumerate(viral_signals[:3], 1):
        content = signal.content
        print(f"  #{i} {content.source_profile}")
        print(f"     📊 {content.views:,} views | {content.likes:,} likes | {content.shares:,} shares")
        print(f"     🔥 Score: {signal.viral_score:.2f} | Growth: {signal.growth_rate:.1f}%")
        print()
    
    # 2. PROCESSAMENTO
    print("⚙️  FASE 2: Processamento")
    print("-" * 70)
    
    processor = RecipeProcessor()
    recipes = []
    
    for i, signal in enumerate(viral_signals, 1):
        print(f"  [{i}/{len(viral_signals)}] Processando {signal.content.source_profile}...", end=" ")
        
        recipe = await processor.process_viral_signal(signal)
        
        if recipe:
            recipes.append(recipe)
            print("✓")
        else:
            print("✗")
    
    print()
    print(f"✓ Processadas: {len(recipes)} receitas")
    print()
    
    if recipes:
        print("📝 Exemplo de receita processada:")
        print("-" * 70)
        example = recipes[0]
        print(f"Título: {example.title}")
        print(f"Categoria: {example.category.value}")
        print(f"Dificuldade: {example.difficulty.value}")
        print(f"Tempo Total: {example.total_time_minutes} minutos")
        print(f"Ingredientes: {len(example.ingredients)}")
        print(f"Porções: {example.servings}")
        print(f"Custo Estimado: {example.estimated_cost}")
        print(f"Prioridade: {example.publish_recommendation.priority.value}")
        print()
    
    # 3. DEDUPLICAÇÃO
    print("🔍 FASE 3: Deduplicação")
    print("-" * 70)
    
    deduplicator = DeduplicationService()
    unique_recipes = []
    
    for recipe in recipes:
        is_dup, reason = deduplicator.is_duplicate(recipe, unique_recipes)
        
        if not is_dup:
            unique_recipes.append(recipe)
            deduplicator.mark_as_seen(recipe)
    
    print(f"✓ Únicas: {len(unique_recipes)} (removidas {len(recipes) - len(unique_recipes)} duplicatas)")
    print()
    
    # 4. PUBLICAÇÃO
    print("📤 FASE 4: Publicação (simulada)")
    print("-" * 70)
    
    publisher = PublisherService()
    
    for recipe in unique_recipes[:5]:  # Limitar a 5
        status = "✓ Publicada" if recipe.publish_recommendation.publish else "⏳ Pendente"
        priority = "🔥" if recipe.publish_recommendation.priority.value == "viral" else "📝"
        print(f"  {priority} {status}: {recipe.title}")
    
    print()
    
    # RESUMO
    print("=" * 70)
    print("📊 RESUMO DO TESTE")
    print("=" * 70)
    print(f"Sinais Virais Detectados: {len(viral_signals)}")
    print(f"Receitas Processadas: {len(recipes)}")
    print(f"Receitas Únicas: {len(unique_recipes)}")
    print(f"Para Publicação: {sum(1 for r in unique_recipes if r.publish_recommendation.publish)}")
    print(f"Pendente Aprovação: {sum(1 for r in unique_recipes if not r.publish_recommendation.publish)}")
    print()
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print()
    
    # Cleanup
    await monitor_coord.close_all()
    await publisher.close()


if __name__ == "__main__":
    try:
        asyncio.run(test_system())
    except KeyboardInterrupt:
        print("\n⚠️  Teste interrompido")
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
