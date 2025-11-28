"""
Monitor de TikTok - rastreia receitas virais no TikTok.
"""
import asyncio
import random
from typing import List
from datetime import datetime, timedelta
import aiohttp
from bs4 import BeautifulSoup

from src.monitors.base_monitor import BaseMonitor
from src.models import RawSocialContent, SourceType
from src.utils.helpers import extract_hashtags, extract_mentions
from config.settings import config


class TikTokMonitor(BaseMonitor):
    """Monitor para rastrear receitas virais no TikTok"""
    
    def __init__(self):
        super().__init__()
        self.api_key = config.TIKTOK_API_KEY
        self.use_api = bool(self.api_key)
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Retorna ou cria session HTTP"""
        if self.session is None or self.session.closed:
            headers = {
                'User-Agent': config.USER_AGENT,
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def fetch_trending_content(self) -> List[RawSocialContent]:
        """Busca conteúdo em trending do TikTok"""
        if config.MOCK_EXTERNAL_APIS:
            return await self._fetch_mock_content()
        
        if self.use_api:
            return await self._fetch_via_api()
        else:
            return await self._fetch_via_scraping()
    
    async def fetch_by_hashtag(self, hashtag: str) -> List[RawSocialContent]:
        """Busca conteúdo por hashtag no TikTok"""
        if config.MOCK_EXTERNAL_APIS:
            return await self._fetch_mock_content(hashtag=hashtag)
        
        if self.use_api:
            return await self._fetch_hashtag_via_api(hashtag)
        else:
            return await self._fetch_hashtag_via_scraping(hashtag)
    
    async def _fetch_via_api(self) -> List[RawSocialContent]:
        """Busca usando TikTok API oficial (se disponível)"""
        self.logger.info("Buscando via TikTok API")
        
        try:
            session = await self._get_session()
            
            # Exemplo de endpoint (ajustar conforme API real)
            url = "https://open-api.tiktok.com/v1/trending/"
            params = {
                'access_token': self.api_key,
                'category': 'food',
                'count': 50
            }
            
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_api_response(data)
                else:
                    self.logger.error(f"API retornou status {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Erro ao buscar via API: {e}")
            return []
    
    async def _fetch_via_scraping(self) -> List[RawSocialContent]:
        """
        Busca via scraping público (sem autenticação).
        NOTA: TikTok tem proteções anti-bot. Em produção, usar:
        - Playwright/Selenium com navegador real
        - Serviços de scraping especializados
        - APIs não-oficiais confiáveis
        """
        self.logger.info("Buscando via scraping (modo limitado)")
        
        if not config.ENABLE_SCRAPING:
            self.logger.warning("Scraping desabilitado nas configurações")
            return []
        
        try:
            # Em produção real, usar Playwright ou serviço especializado
            # Aqui é apenas estrutura de exemplo
            session = await self._get_session()
            
            # Delay para respeitar rate limits
            await asyncio.sleep(config.REQUEST_DELAY_SECONDS)
            
            # URLs de exemplo (ajustar para real)
            urls_to_scrape = [
                "https://www.tiktok.com/tag/receita",
                "https://www.tiktok.com/tag/tiktokfood",
            ]
            
            all_content = []
            for url in urls_to_scrape[:2]:  # Limitar em desenvolvimento
                try:
                    content = await self._scrape_url(url, session)
                    all_content.extend(content)
                    await asyncio.sleep(config.REQUEST_DELAY_SECONDS)
                except Exception as e:
                    self.logger.error(f"Erro ao scrape {url}: {e}")
            
            return all_content
            
        except Exception as e:
            self.logger.error(f"Erro geral no scraping: {e}")
            return []
    
    async def _scrape_url(self, url: str, session: aiohttp.ClientSession) -> List[RawSocialContent]:
        """Scrape uma URL específica"""
        try:
            async with session.get(url, timeout=30) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                # Parsear conteúdo (ajustar seletores conforme HTML real)
                # Este é apenas um exemplo estrutural
                content_list = []
                
                # TikTok renderiza via JavaScript, então scraping simples não funciona bem
                # Em produção, usar Playwright
                self.logger.warning("Scraping direto de TikTok requer JavaScript rendering")
                
                return content_list
                
        except Exception as e:
            self.logger.error(f"Erro ao scrape {url}: {e}")
            return []
    
    async def _fetch_hashtag_via_api(self, hashtag: str) -> List[RawSocialContent]:
        """Busca hashtag via API"""
        self.logger.info(f"Buscando #{hashtag} via API")
        # Implementação similar a _fetch_via_api
        return []
    
    async def _fetch_hashtag_via_scraping(self, hashtag: str) -> List[RawSocialContent]:
        """Busca hashtag via scraping"""
        self.logger.info(f"Buscando #{hashtag} via scraping")
        url = f"https://www.tiktok.com/tag/{hashtag}"
        session = await self._get_session()
        return await self._scrape_url(url, session)
    
    async def _fetch_mock_content(self, hashtag: str = None) -> List[RawSocialContent]:
        """Retorna dados mock para desenvolvimento/testes"""
        self.logger.info(f"Gerando conteúdo MOCK para TikTok{f' (#{hashtag})' if hashtag else ''}")
        
        mock_data = []
        num_items = random.randint(3, 8)
        
        for i in range(num_items):
            views = random.randint(50000, 5000000)
            likes = int(views * random.uniform(0.03, 0.12))
            shares = int(views * random.uniform(0.005, 0.03))
            comments = int(views * random.uniform(0.01, 0.05))
            
            content = RawSocialContent(
                source_type=SourceType.TIKTOK,
                source_url=f"https://tiktok.com/@chef{i}/video/{random.randint(1000000, 9999999)}",
                source_profile=f"@chef_viral_{i}",
                raw_title=f"Receita viral {i+1}",
                raw_caption=f"Essa receita tá bombando! 🔥 Vem fazer! #{hashtag or 'receita'} #tiktokfood #receitafacil",
                media_url=f"https://cdn.tiktok.com/video/{random.randint(1000, 9999)}.mp4",
                published_at=datetime.utcnow() - timedelta(hours=random.randint(1, 12)),
                views=views,
                likes=likes,
                shares=shares,
                comments=comments,
                hashtags=[hashtag or 'receita', 'tiktokfood', 'receitafacil'],
                mentions=[],
                sound_id=f"sound_{random.randint(1000, 9999)}",
                sound_name="trending_sound_name"
            )
            mock_data.append(content)
        
        return mock_data
    
    def _parse_api_response(self, data: dict) -> List[RawSocialContent]:
        """Parse resposta da API do TikTok"""
        content_list = []
        
        try:
            videos = data.get('data', {}).get('videos', [])
            
            for video in videos:
                content = RawSocialContent(
                    source_type=SourceType.TIKTOK,
                    source_url=video.get('share_url', ''),
                    source_profile=f"@{video.get('author', {}).get('unique_id', 'unknown')}",
                    raw_title=video.get('desc', ''),
                    raw_caption=video.get('desc', ''),
                    media_url=video.get('video', {}).get('play_addr', ''),
                    published_at=datetime.fromtimestamp(video.get('create_time', 0)),
                    views=video.get('statistics', {}).get('play_count', 0),
                    likes=video.get('statistics', {}).get('digg_count', 0),
                    shares=video.get('statistics', {}).get('share_count', 0),
                    comments=video.get('statistics', {}).get('comment_count', 0),
                    hashtags=extract_hashtags(video.get('desc', '')),
                    mentions=extract_mentions(video.get('desc', '')),
                    sound_id=video.get('music', {}).get('id', ''),
                    sound_name=video.get('music', {}).get('title', '')
                )
                content_list.append(content)
                
        except Exception as e:
            self.logger.error(f"Erro ao parse API response: {e}")
        
        return content_list
    
    def _get_relevant_hashtags(self) -> List[str]:
        """Retorna hashtags do TikTok configuradas"""
        return config.TIKTOK_HASHTAGS
    
    async def close(self):
        """Fecha a sessão HTTP"""
        if self.session and not self.session.closed:
            await self.session.close()
