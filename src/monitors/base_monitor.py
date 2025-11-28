"""
Monitor base - classe abstrata para todos os monitores.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from src.models import RawSocialContent, ViralSignal
from config.settings import config


class BaseMonitor(ABC):
    """Classe base abstrata para todos os monitores de redes sociais"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.logger = logger.bind(monitor=self.name)
        self.last_check = None
        self.total_scanned = 0
        self.total_viral_found = 0
    
    @abstractmethod
    async def fetch_trending_content(self) -> List[RawSocialContent]:
        """
        Busca conteúdo em alta na plataforma.
        Deve ser implementado por cada monitor específico.
        """
        pass
    
    @abstractmethod
    async def fetch_by_hashtag(self, hashtag: str) -> List[RawSocialContent]:
        """
        Busca conteúdo por hashtag específica.
        Deve ser implementado por cada monitor específico.
        """
        pass
    
    def is_viral(self, content: RawSocialContent) -> ViralSignal:
        """
        Determina se o conteúdo é viral baseado em múltiplos sinais.
        Aplica thresholds configuráveis.
        """
        signals = []
        viral_score = 0.0
        
        # Calcular taxa de crescimento (simplificado - assume baseline)
        time_diff = (datetime.utcnow() - content.published_at).total_seconds() / 3600  # horas
        
        if time_diff == 0:
            time_diff = 0.1  # Evitar divisão por zero
        
        # Views por hora
        views_per_hour = content.views / time_diff if time_diff > 0 else content.views
        
        # Engagement rate
        total_engagement = content.likes + content.shares + content.comments
        engagement_rate = (total_engagement / content.views * 100) if content.views > 0 else 0
        
        # Verificar thresholds
        if content.views >= config.THRESHOLD_VIRAL_VIEWS:
            signals.append(f"views:{content.views}")
            viral_score += 0.3
        
        if content.likes >= config.THRESHOLD_VIRAL_LIKES:
            signals.append(f"likes:{content.likes}")
            viral_score += 0.2
        
        if content.shares >= config.THRESHOLD_VIRAL_SHARES:
            signals.append(f"shares:{content.shares}")
            viral_score += 0.25
        
        # Growth rate baseado em views/hora
        baseline_views_per_hour = config.THRESHOLD_VIRAL_VIEWS / config.TIME_WINDOW_HOURS
        growth_rate = ((views_per_hour - baseline_views_per_hour) / baseline_views_per_hour * 100) if baseline_views_per_hour > 0 else 0
        
        if growth_rate >= config.THRESHOLD_GROWTH_RATE:
            signals.append(f"growth_rate:{growth_rate:.1f}%")
            viral_score += 0.25
        
        # Engagement bonus
        if engagement_rate > 5:  # >5% é muito bom
            signals.append(f"high_engagement:{engagement_rate:.1f}%")
            viral_score += 0.1
        
        # Determinar se é viral (precisa de pelo menos 2 sinais fortes)
        is_viral = len(signals) >= 2 and viral_score >= 0.5
        
        reason = None
        if not is_viral:
            if len(signals) == 0:
                reason = "Nenhum sinal de viralização detectado"
            elif viral_score < 0.5:
                reason = f"Score viral insuficiente: {viral_score:.2f}"
            else:
                reason = f"Apenas {len(signals)} sinais detectados (mínimo: 2)"
        
        return ViralSignal(
            content=content,
            is_viral=is_viral,
            viral_score=min(viral_score, 1.0),
            growth_rate=growth_rate,
            time_window_hours=int(time_diff),
            signals_detected=signals,
            reason=reason
        )
    
    async def scan(self) -> List[ViralSignal]:
        """
        Executa varredura completa: busca trending + hashtags.
        Retorna apenas conteúdo viral.
        """
        self.logger.info(f"Iniciando varredura em {self.name}")
        all_content: List[RawSocialContent] = []
        
        try:
            # Buscar trending
            trending = await self.fetch_trending_content()
            all_content.extend(trending)
            self.logger.info(f"Encontrados {len(trending)} itens em trending")
            
            # Buscar por hashtags
            hashtags = self._get_relevant_hashtags()
            for hashtag in hashtags:
                try:
                    hashtag_content = await self.fetch_by_hashtag(hashtag)
                    all_content.extend(hashtag_content)
                    self.logger.debug(f"Hashtag #{hashtag}: {len(hashtag_content)} itens")
                except Exception as e:
                    self.logger.error(f"Erro ao buscar hashtag #{hashtag}: {e}")
            
            # Remover duplicatas (mesmo URL)
            unique_content = self._deduplicate_by_url(all_content)
            self.logger.info(f"Total único: {len(unique_content)} itens")
            
            # Filtrar apenas viral
            viral_signals = []
            for content in unique_content:
                signal = self.is_viral(content)
                if signal.is_viral:
                    viral_signals.append(signal)
                    self.logger.info(
                        f"🔥 VIRAL DETECTADO: {content.source_profile} | "
                        f"Views: {content.views} | Score: {signal.viral_score:.2f}"
                    )
            
            self.total_scanned += len(unique_content)
            self.total_viral_found += len(viral_signals)
            self.last_check = datetime.utcnow()
            
            self.logger.info(
                f"Varredura concluída: {len(viral_signals)} virais de {len(unique_content)} analisados"
            )
            
            return viral_signals
            
        except Exception as e:
            self.logger.error(f"Erro durante varredura: {e}", exc_info=True)
            return []
    
    def _get_relevant_hashtags(self) -> List[str]:
        """Retorna hashtags relevantes baseadas no tipo de monitor"""
        # Sobrescrever em subclasses se necessário
        return []
    
    def _deduplicate_by_url(self, content_list: List[RawSocialContent]) -> List[RawSocialContent]:
        """Remove duplicatas baseado em URL"""
        seen_urls = set()
        unique = []
        
        for content in content_list:
            if content.source_url not in seen_urls:
                seen_urls.add(content.source_url)
                unique.append(content)
        
        return unique
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do monitor"""
        return {
            "monitor": self.name,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "total_scanned": self.total_scanned,
            "total_viral_found": self.total_viral_found,
            "viral_rate": f"{(self.total_viral_found / self.total_scanned * 100):.2f}%" if self.total_scanned > 0 else "0%"
        }
