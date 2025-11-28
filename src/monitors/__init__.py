"""
Coordenador de monitores - gerencia execução paralela de todos os monitores.
"""
import asyncio
from typing import List, Dict, Any
from loguru import logger

from src.monitors.tiktok_monitor import TikTokMonitor
from src.monitors.instagram_monitor import InstagramMonitor
from src.monitors.rss_monitor import RSSMonitor
from src.models import ViralSignal


class MonitorCoordinator:
    """Coordena a execução de todos os monitores em paralelo"""
    
    def __init__(self):
        self.monitors = [
            TikTokMonitor(),
            InstagramMonitor(),
            RSSMonitor()
        ]
        self.logger = logger.bind(component="MonitorCoordinator")
    
    async def run_all_monitors(self) -> List[ViralSignal]:
        """
        Executa todos os monitores em paralelo e consolida resultados.
        Retorna lista de sinais virais detectados.
        """
        self.logger.info(f"Iniciando varredura com {len(self.monitors)} monitores")
        
        try:
            # Executar todos os monitores em paralelo
            tasks = [monitor.scan() for monitor in self.monitors]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Consolidar resultados
            all_viral_signals: List[ViralSignal] = []
            
            for i, result in enumerate(results):
                monitor_name = self.monitors[i].name
                
                if isinstance(result, Exception):
                    self.logger.error(f"Monitor {monitor_name} falhou: {result}")
                    continue
                
                if isinstance(result, list):
                    all_viral_signals.extend(result)
                    self.logger.info(
                        f"✓ {monitor_name}: {len(result)} virais detectados"
                    )
            
            # Remover duplicatas cross-platform (mesmo conteúdo em múltiplas plataformas)
            unique_signals = self._deduplicate_signals(all_viral_signals)
            
            self.logger.info(
                f"Varredura completa: {len(unique_signals)} sinais virais únicos "
                f"(de {len(all_viral_signals)} totais)"
            )
            
            return unique_signals
            
        except Exception as e:
            self.logger.error(f"Erro crítico no coordenador: {e}", exc_info=True)
            return []
    
    def _deduplicate_signals(self, signals: List[ViralSignal]) -> List[ViralSignal]:
        """
        Remove sinais duplicados baseado em:
        - URL exata igual
        - Título muito similar + mesmo perfil
        """
        if not signals:
            return []
        
        unique_signals = []
        seen_urls = set()
        seen_fingerprints = set()
        
        for signal in signals:
            url = signal.content.source_url
            
            # Verificar URL exata
            if url in seen_urls:
                continue
            
            # Criar fingerprint simples: profile + primeiras palavras do título
            title_words = signal.content.raw_title[:50].lower() if signal.content.raw_title else ""
            fingerprint = f"{signal.content.source_profile}:{title_words}"
            
            if fingerprint in seen_fingerprints:
                self.logger.debug(f"Duplicata detectada: {signal.content.source_profile}")
                continue
            
            seen_urls.add(url)
            seen_fingerprints.add(fingerprint)
            unique_signals.append(signal)
        
        removed = len(signals) - len(unique_signals)
        if removed > 0:
            self.logger.info(f"Removidas {removed} duplicatas cross-platform")
        
        return unique_signals
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de todos os monitores"""
        stats = {
            "monitors": [monitor.get_stats() for monitor in self.monitors],
            "total_monitors": len(self.monitors)
        }
        return stats
    
    async def close_all(self):
        """Fecha todos os monitores gracefully"""
        self.logger.info("Fechando todos os monitores...")
        
        close_tasks = []
        for monitor in self.monitors:
            if hasattr(monitor, 'close'):
                close_tasks.append(monitor.close())
        
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
        
        self.logger.info("Monitores fechados")
