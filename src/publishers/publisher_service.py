"""
Sistema de publicação - publica receitas no CMS ou envia para aprovação.
"""
import asyncio
import aiohttp
from typing import List, Dict, Any
from loguru import logger

from src.models import Recipe
from config.settings import config


class PublisherService:
    """Serviço de publicação de receitas"""
    
    def __init__(self):
        self.logger = logger.bind(service="Publisher")
        self.session = None
        self.pending_approval = []
        self.published_count = 0
        self.failed_count = 0
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Retorna ou cria session HTTP"""
        if self.session is None or self.session.closed:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {config.CMS_API_KEY}' if config.CMS_API_KEY else ''
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def publish_recipe(self, recipe: Recipe) -> bool:
        """
        Publica receita ou envia para aprovação conforme configuração.
        Retorna True se sucesso.
        """
        try:
            # Verificar se deve publicar automaticamente
            if config.AUTO_MODE and recipe.publish_recommendation.publish:
                success = await self._publish_to_cms(recipe)
                if success:
                    self.published_count += 1
                    self.logger.info(f"✓ Publicada: {recipe.title}")
                else:
                    self.failed_count += 1
                return success
            else:
                # Enviar para aprovação admin
                self.pending_approval.append(recipe)
                self.logger.info(f"→ Pendente aprovação: {recipe.title}")
                return True
                
        except Exception as e:
            self.logger.error(f"Erro ao publicar {recipe.title}: {e}")
            self.failed_count += 1
            return False
    
    async def _publish_to_cms(self, recipe: Recipe) -> bool:
        """Publica receita no CMS via API"""
        try:
            session = await self._get_session()
            
            # Converter para dict
            payload = recipe.dict()
            
            async with session.post(
                config.CMS_ENDPOINT,
                json=payload,
                timeout=30
            ) as response:
                if response.status in [200, 201]:
                    self.logger.info(f"Receita publicada no CMS: {recipe.slug}")
                    return True
                else:
                    error_text = await response.text()
                    self.logger.error(f"CMS retornou {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Erro ao publicar no CMS: {e}")
            return False
    
    async def publish_batch(self, recipes: List[Recipe]) -> Dict[str, int]:
        """Publica múltiplas receitas em lote"""
        self.logger.info(f"Publicando lote de {len(recipes)} receitas")
        
        results = {
            'success': 0,
            'failed': 0,
            'pending': 0
        }
        
        for recipe in recipes:
            success = await self.publish_recipe(recipe)
            if success:
                if config.AUTO_MODE and recipe.publish_recommendation.publish:
                    results['success'] += 1
                else:
                    results['pending'] += 1
            else:
                results['failed'] += 1
        
        return results
    
    def get_pending_recipes(self) -> List[Recipe]:
        """Retorna receitas pendentes de aprovação"""
        return self.pending_approval.copy()
    
    def clear_pending(self):
        """Limpa lista de pendentes"""
        self.pending_approval.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de publicação"""
        return {
            'published': self.published_count,
            'failed': self.failed_count,
            'pending': len(self.pending_approval)
        }
    
    async def close(self):
        """Fecha sessão"""
        if self.session and not self.session.closed:
            await self.session.close()
