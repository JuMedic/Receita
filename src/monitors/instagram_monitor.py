"""
Monitor de Instagram - rastreia receitas virais no Instagram (Reels, Posts).
"""
import asyncio
import random
from typing import List
from datetime import datetime, timedelta
import aiohttp

from src.monitors.base_monitor import BaseMonitor
from src.models import RawSocialContent, SourceType
from src.utils.helpers import extract_hashtags, extract_mentions
from config.settings import config


class InstagramMonitor(BaseMonitor):
    """Monitor para rastrear receitas virais no Instagram"""
    
    def __init__(self):
        super().__init__()
        self.access_token = config.INSTAGRAM_GRAPH_API_TOKEN
        self.use_api = bool(self.access_token)
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Retorna ou cria session HTTP"""
        if self.session is None or self.session.closed:
            headers = {
                'User-Agent': config.USER_AGENT,
                'Accept-Language': 'pt-BR,pt;q=0.9',
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def fetch_trending_content(self) -> List[RawSocialContent]:
        """Busca conteúdo em trending do Instagram (Reels no Explore)"""
        if config.MOCK_EXTERNAL_APIS:
            return await self._fetch_mock_content()
        
        if self.use_api:
            return await self._fetch_via_graph_api()
        else:
            return await self._fetch_via_scraping()
    
    async def fetch_by_hashtag(self, hashtag: str) -> List[RawSocialContent]:
        """Busca conteúdo por hashtag no Instagram"""
        if config.MOCK_EXTERNAL_APIS:
            return await self._fetch_mock_content(hashtag=hashtag)
        
        if self.use_api:
            return await self._fetch_hashtag_via_api(hashtag)
        else:
            return await self._fetch_hashtag_via_scraping(hashtag)
    
    async def _fetch_via_graph_api(self) -> List[RawSocialContent]:
        """
        Busca usando Instagram Graph API.
        Requer: Business Account + Facebook Developer App
        """
        self.logger.info("Buscando via Instagram Graph API")
        
        try:
            session = await self._get_session()
            
            # Endpoint para buscar próprio conteúdo ou páginas autorizadas
            # Para trending público, Graph API tem limitações
            url = f"https://graph.instagram.com/me/media"
            params = {
                'access_token': self.access_token,
                'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count,insights.metric(impressions,reach,shares)',
                'limit': 50
            }
            
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_graph_api_response(data)
                else:
                    self.logger.error(f"Graph API retornou status {response.status}")
                    error_data = await response.text()
                    self.logger.error(f"Erro: {error_data}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Erro ao buscar via Graph API: {e}")
            return []
    
    async def _fetch_via_scraping(self) -> List[RawSocialContent]:
        """
        Busca via scraping.
        NOTA: Instagram tem proteções fortes. Recomendado:
        - APIs de terceiros (Apify, RapidAPI)
        - Playwright com login simulado
        - Proxies rotativos
        """
        self.logger.info("Buscando via scraping (modo limitado)")
        
        if not config.ENABLE_SCRAPING:
            self.logger.warning("Scraping desabilitado")
            return []
        
        try:
            # Instagram requer autenticação para a maioria do conteúdo
            # Scraping público é muito limitado
            self.logger.warning("Scraping direto de Instagram é limitado sem autenticação")
            return []
            
        except Exception as e:
            self.logger.error(f"Erro no scraping: {e}")
            return []
    
    async def _fetch_hashtag_via_api(self, hashtag: str) -> List[RawSocialContent]:
        """
        Busca hashtag via Graph API.
        Limitado a Business Accounts com permissões específicas.
        """
        self.logger.info(f"Buscando #{hashtag} via Graph API")
        
        try:
            session = await self._get_session()
            
            # Buscar hashtag ID primeiro
            search_url = f"https://graph.instagram.com/ig_hashtag_search"
            search_params = {
                'user_id': 'me',  # Requer user_id de Business Account
                'q': hashtag,
                'access_token': self.access_token
            }
            
            async with session.get(search_url, params=search_params, timeout=30) as response:
                if response.status != 200:
                    return []
                
                search_data = await response.json()
                if not search_data.get('data'):
                    return []
                
                hashtag_id = search_data['data'][0]['id']
            
            # Buscar posts recentes da hashtag
            posts_url = f"https://graph.instagram.com/{hashtag_id}/recent_media"
            posts_params = {
                'user_id': 'me',
                'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
                'access_token': self.access_token,
                'limit': 50
            }
            
            async with session.get(posts_url, params=posts_params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_graph_api_response(data)
                    
        except Exception as e:
            self.logger.error(f"Erro ao buscar hashtag via API: {e}")
            return []
    
    async def _fetch_hashtag_via_scraping(self, hashtag: str) -> List[RawSocialContent]:
        """Scraping de hashtag"""
        self.logger.warning(f"Scraping de #{hashtag} no Instagram não implementado")
        return []
    
    async def _fetch_mock_content(self, hashtag: str = None) -> List[RawSocialContent]:
        """Gera dados mock para desenvolvimento"""
        self.logger.info(f"Gerando conteúdo MOCK para Instagram{f' (#{hashtag})' if hashtag else ''}")
        
        mock_data = []
        num_items = random.randint(3, 7)
        
        for i in range(num_items):
            views = random.randint(30000, 3000000)
            likes = int(views * random.uniform(0.05, 0.15))
            shares = int(views * random.uniform(0.01, 0.04))
            comments = int(views * random.uniform(0.02, 0.06))
            
            is_reel = random.choice([True, True, False])  # 66% Reels
            
            content = RawSocialContent(
                source_type=SourceType.INSTAGRAM,
                source_url=f"https://instagram.com/p/ABC{random.randint(100, 999)}XYZ/",
                source_profile=f"@foodlover_{i}",
                raw_title=f"Receita deliciosa {i+1}" if not is_reel else f"Reel: Receita rápida {i+1}",
                raw_caption=f"Receita incrível! 😍 Salva aí pra fazer depois! 💕\n\n#{hashtag or 'receitas'} #reels #comida #receitasfit",
                media_url=f"https://scontent.cdninstagram.com/v/t{'51' if is_reel else '50'}.{random.randint(1000, 9999)}.jpg",
                published_at=datetime.utcnow() - timedelta(hours=random.randint(1, 18)),
                views=views,
                likes=likes,
                shares=shares,
                comments=comments,
                hashtags=[hashtag or 'receitas', 'reels', 'comida', 'receitasfit'],
                mentions=[]
            )
            mock_data.append(content)
        
        return mock_data
    
    def _parse_graph_api_response(self, data: dict) -> List[RawSocialContent]:
        """Parse resposta da Graph API"""
        content_list = []
        
        try:
            media_items = data.get('data', [])
            
            for item in media_items:
                # Pegar insights se disponível
                insights = item.get('insights', {}).get('data', [])
                impressions = 0
                shares = 0
                
                for insight in insights:
                    if insight.get('name') == 'impressions':
                        impressions = insight.get('values', [{}])[0].get('value', 0)
                    elif insight.get('name') == 'shares':
                        shares = insight.get('values', [{}])[0].get('value', 0)
                
                caption = item.get('caption', '')
                
                content = RawSocialContent(
                    source_type=SourceType.INSTAGRAM,
                    source_url=item.get('permalink', ''),
                    source_profile='@' + item.get('username', 'unknown'),
                    raw_title=caption[:100] if caption else '',
                    raw_caption=caption,
                    media_url=item.get('media_url', ''),
                    published_at=datetime.fromisoformat(item.get('timestamp', '').replace('Z', '+00:00')),
                    views=impressions,  # Instagram não expõe views públicas, usar impressions
                    likes=item.get('like_count', 0),
                    shares=shares,
                    comments=item.get('comments_count', 0),
                    hashtags=extract_hashtags(caption),
                    mentions=extract_mentions(caption)
                )
                content_list.append(content)
                
        except Exception as e:
            self.logger.error(f"Erro ao parse Graph API response: {e}")
        
        return content_list
    
    def _get_relevant_hashtags(self) -> List[str]:
        """Retorna hashtags do Instagram configuradas"""
        return config.INSTAGRAM_HASHTAGS
    
    async def close(self):
        """Fecha a sessão HTTP"""
        if self.session and not self.session.closed:
            await self.session.close()
