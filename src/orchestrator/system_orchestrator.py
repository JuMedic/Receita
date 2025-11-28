"""
Orquestrador principal - coordena todo o sistema 24/7.
"""
import asyncio
from datetime import datetime, timedelta
from typing import List
from loguru import logger

from src.monitors import MonitorCoordinator
from src.processors.recipe_processor import RecipeProcessor
from src.utils.deduplication import DeduplicationService
from src.publishers.publisher_service import PublisherService
from src.models import Recipe
from config.settings import config


class SystemOrchestrator:
    """Orquestrador principal do sistema de receitas virais"""
    
    def __init__(self):
        self.logger = logger.bind(component="Orchestrator")
        
        # Componentes
        self.monitor_coordinator = MonitorCoordinator()
        self.processor = RecipeProcessor()
        self.deduplicator = DeduplicationService()
        self.publisher = PublisherService()
        
        # Estado
        self.is_running = False
        self.cycle_count = 0
        self.start_time = None
        self.processed_recipes: List[Recipe] = []
    
    async def start(self):
        """Inicia sistema 24/7"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 INICIANDO SISTEMA DE RECEITAS VIRAIS 24/7")
        self.logger.info("=" * 60)
        self.logger.info(f"Modo: {'AUTOMÁTICO' if config.AUTO_MODE else 'MANUAL (aprovação admin)'}")
        self.logger.info(f"Ciclo: {config.CYCLE_MINUTES} minutos")
        self.logger.info(f"Thresholds: Views≥{config.THRESHOLD_VIRAL_VIEWS}, "
                        f"Likes≥{config.THRESHOLD_VIRAL_LIKES}, "
                        f"Shares≥{config.THRESHOLD_VIRAL_SHARES}")
        self.logger.info("=" * 60)
        
        self.is_running = True
        self.start_time = datetime.utcnow()
        
        try:
            while self.is_running:
                await self._run_cycle()
                
                if self.is_running:
                    self.logger.info(f"💤 Aguardando {config.CYCLE_MINUTES} minutos até próximo ciclo...")
                    await asyncio.sleep(config.CYCLE_MINUTES * 60)
                    
        except KeyboardInterrupt:
            self.logger.info("Interrompido por usuário")
        except Exception as e:
            self.logger.error(f"Erro crítico no orquestrador: {e}", exc_info=True)
        finally:
            await self.stop()
    
    async def _run_cycle(self):
        """Executa um ciclo completo de monitoramento→processamento→publicação"""
        self.cycle_count += 1
        cycle_start = datetime.utcnow()
        
        self.logger.info("=" * 60)
        self.logger.info(f"🔄 CICLO #{self.cycle_count} - {cycle_start.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        self.logger.info("=" * 60)
        
        try:
            # 1. MONITORAMENTO
            self.logger.info("📡 FASE 1: Monitoramento de plataformas")
            viral_signals = await self.monitor_coordinator.run_all_monitors()
            
            if not viral_signals:
                self.logger.warning("Nenhum conteúdo viral detectado neste ciclo")
                return
            
            self.logger.info(f"✓ Detectados {len(viral_signals)} sinais virais")
            
            # 2. PROCESSAMENTO
            self.logger.info("⚙️  FASE 2: Processamento de receitas")
            processed_recipes = []
            
            for i, signal in enumerate(viral_signals, 1):
                self.logger.info(f"[{i}/{len(viral_signals)}] Processando {signal.content.source_profile}")
                
                recipe = await self.processor.process_viral_signal(signal)
                
                if recipe:
                    processed_recipes.append(recipe)
                else:
                    self.logger.warning(f"Falha ao processar sinal de {signal.content.source_profile}")
            
            self.logger.info(f"✓ Processadas {len(processed_recipes)}/{len(viral_signals)} receitas")
            
            if not processed_recipes:
                self.logger.warning("Nenhuma receita válida processada")
                return
            
            # 3. DEDUPLICAÇÃO
            self.logger.info("🔍 FASE 3: Deduplicação")
            unique_recipes = []
            
            for recipe in processed_recipes:
                is_duplicate, reason = self.deduplicator.is_duplicate(
                    recipe,
                    self.processed_recipes
                )
                
                if is_duplicate:
                    self.logger.warning(f"❌ Duplicata: {recipe.title} - {reason}")
                    recipe.meta.duplicate = True
                    recipe.publish_recommendation.publish = False
                else:
                    unique_recipes.append(recipe)
                    self.deduplicator.mark_as_seen(recipe)
            
            self.logger.info(f"✓ {len(unique_recipes)} receitas únicas (removidas {len(processed_recipes) - len(unique_recipes)} duplicatas)")
            
            if not unique_recipes:
                self.logger.warning("Todas as receitas eram duplicadas")
                return
            
            # 4. PUBLICAÇÃO
            self.logger.info("📤 FASE 4: Publicação")
            publish_results = await self.publisher.publish_batch(unique_recipes)
            
            self.logger.info(
                f"✓ Publicação concluída: "
                f"{publish_results['success']} publicadas, "
                f"{publish_results['pending']} pendentes, "
                f"{publish_results['failed']} falharam"
            )
            
            # Adicionar ao histórico
            self.processed_recipes.extend(unique_recipes)
            
            # Limitar histórico
            if len(self.processed_recipes) > 500:
                self.processed_recipes = self.processed_recipes[-250:]
            
            # Resumo do ciclo
            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
            self._log_cycle_summary(cycle_duration, viral_signals, unique_recipes, publish_results)
            
        except Exception as e:
            self.logger.error(f"Erro durante ciclo #{self.cycle_count}: {e}", exc_info=True)
    
    def _log_cycle_summary(self, duration: float, signals, recipes, results):
        """Registra resumo do ciclo"""
        self.logger.info("=" * 60)
        self.logger.info(f"📊 RESUMO DO CICLO #{self.cycle_count}")
        self.logger.info("-" * 60)
        self.logger.info(f"⏱️  Duração: {duration:.1f}s")
        self.logger.info(f"🔥 Sinais virais: {len(signals)}")
        self.logger.info(f"📝 Receitas processadas: {len(recipes)}")
        self.logger.info(f"✅ Publicadas: {results['success']}")
        self.logger.info(f"⏳ Pendentes: {results['pending']}")
        self.logger.info(f"❌ Falhas: {results['failed']}")
        
        # Estatísticas globais
        uptime = datetime.utcnow() - self.start_time if self.start_time else timedelta(0)
        self.logger.info("-" * 60)
        self.logger.info(f"📈 ESTATÍSTICAS GLOBAIS")
        self.logger.info(f"🕐 Uptime: {uptime}")
        self.logger.info(f"🔄 Total de ciclos: {self.cycle_count}")
        self.logger.info(f"📚 Receitas no histórico: {len(self.processed_recipes)}")
        self.logger.info("=" * 60)
    
    async def stop(self):
        """Para o sistema gracefully"""
        self.logger.info("🛑 Parando sistema...")
        self.is_running = False
        
        # Fechar componentes
        await self.monitor_coordinator.close_all()
        await self.publisher.close()
        
        # Log final
        if self.start_time:
            uptime = datetime.utcnow() - self.start_time
            self.logger.info(f"Sistema executou por {uptime}")
            self.logger.info(f"Total de ciclos: {self.cycle_count}")
            self.logger.info(f"Total de receitas processadas: {len(self.processed_recipes)}")
        
        self.logger.info("✓ Sistema parado")
    
    def get_stats(self):
        """Retorna estatísticas completas do sistema"""
        return {
            'uptime': str(datetime.utcnow() - self.start_time) if self.start_time else '0',
            'cycles': self.cycle_count,
            'recipes_processed': len(self.processed_recipes),
            'monitors': self.monitor_coordinator.get_all_stats(),
            'publisher': self.publisher.get_stats(),
            'pending_approval': len(self.publisher.get_pending_recipes())
        }
