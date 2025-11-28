"""
Monitor de RSS - rastreia receitas de feeds RSS que indexam trends.
"""
import asyncio
import random
from typing import List
from datetime import datetime, timedelta
import feedparser
import aiohttp

from src.monitors.base_monitor import BaseMonitor
from src.models import RawSocialContent, SourceType
from src.utils.helpers import extract_hashtags, extract_mentions, clean_text
from config.settings import config


class RSSMonitor(BaseMonitor):
    """Monitor para rastrear receitas de feeds RSS"""
    
    def __init__(self):
        super().__init__()
        self.feed_urls = config.RSS_FEED_URLS
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Retorna ou cria session HTTP"""
        if self.session is None or self.session.closed:
            headers = {'User-Agent': config.USER_AGENT}
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def fetch_trending_content(self) -> List[RawSocialContent]:
        """Busca conteúdo de todos os feeds RSS configurados"""
        if config.MOCK_EXTERNAL_APIS or not self.feed_urls:
            return await self._fetch_mock_content()
        
        all_content = []
        
        for feed_url in self.feed_urls:
            try:
                content = await self._fetch_feed(feed_url)
                all_content.extend(content)
                self.logger.info(f"Feed {feed_url}: {len(content)} itens")
                
                # Delay entre feeds
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Erro ao buscar feed {feed_url}: {e}")
        
        return all_content
    
    async def fetch_by_hashtag(self, hashtag: str) -> List[RawSocialContent]:
        """
        RSS não suporta busca por hashtag diretamente.
        Retorna conteúdo que contém a hashtag.
        """
        all_content = await self.fetch_trending_content()
        
        # Filtrar por hashtag
        filtered = [
            content for content in all_content
            if hashtag.lower() in [tag.lower() for tag in content.hashtags]
        ]
        
        return filtered
    
    async def _fetch_feed(self, feed_url: str) -> List[RawSocialContent]:
        """Busca e parse um feed RSS específico"""
        try:
            session = await self._get_session()
            
            async with session.get(feed_url, timeout=30) as response:
                if response.status != 200:
                    self.logger.error(f"Feed retornou status {response.status}")
                    return []
                
                xml_content = await response.text()
            
            # Parse RSS com feedparser
            feed = feedparser.parse(xml_content)
            
            if feed.bozo:  # bozo=True significa erro no parse
                self.logger.warning(f"Feed mal formatado: {feed_url}")
            
            content_list = []
            
            for entry in feed.entries[:50]:  # Limitar a 50 itens por feed
                try:
                    content = self._parse_entry(entry, feed)
                    if content and self._is_recipe_related(content):
                        content_list.append(content)
                except Exception as e:
                    self.logger.error(f"Erro ao parse entrada: {e}")
            
            return content_list
            
        except Exception as e:
            self.logger.error(f"Erro ao fetch feed {feed_url}: {e}")
            return []
    
    def _parse_entry(self, entry, feed) -> RawSocialContent:
        """Parse uma entrada do feed RSS"""
        # Extrair dados
        title = clean_text(entry.get('title', ''))
        description = clean_text(entry.get('description', entry.get('summary', '')))
        link = entry.get('link', '')
        
        # Data de publicação
        published = entry.get('published_parsed') or entry.get('updated_parsed')
        if published:
            published_at = datetime(*published[:6])
        else:
            published_at = datetime.utcnow()
        
        # Tentar extrair imagem
        media_url = None
        if hasattr(entry, 'media_content') and entry.media_content:
            media_url = entry.media_content[0].get('url')
        elif hasattr(entry, 'enclosures') and entry.enclosures:
            media_url = entry.enclosures[0].get('href')
        
        # Autor/perfil
        author = entry.get('author', feed.feed.get('title', 'RSS Feed'))
        
        # Tentar extrair métricas (alguns feeds RSS incluem)
        # Caso contrário, usar valores padrão baixos
        views = self._extract_metric(entry, ['views', 'view_count'])
        likes = self._extract_metric(entry, ['likes', 'like_count', 'favorites'])
        shares = self._extract_metric(entry, ['shares', 'share_count'])
        comments = self._extract_metric(entry, ['comments', 'comment_count'])
        
        # Hashtags e mentions
        full_text = f"{title} {description}"
        hashtags = extract_hashtags(full_text)
        mentions = extract_mentions(full_text)
        
        content = RawSocialContent(
            source_type=SourceType.RSS,
            source_url=link,
            source_profile=author,
            raw_title=title,
            raw_caption=description,
            media_url=media_url or '',
            published_at=published_at,
            views=views,
            likes=likes,
            shares=shares,
            comments=comments,
            hashtags=hashtags,
            mentions=mentions
        )
        
        return content
    
    def _extract_metric(self, entry, field_names: List[str]) -> int:
        """Tenta extrair métrica de várias possíveis localizações"""
        for field in field_names:
            if hasattr(entry, field):
                try:
                    return int(getattr(entry, field))
                except (ValueError, TypeError):
                    pass
        return 0
    
    def _is_recipe_related(self, content: RawSocialContent) -> bool:
        """
        Verifica se o conteúdo é relacionado a receitas.
        Busca keywords em título/descrição.
        """
        recipe_keywords = [
            'receita', 'recipe', 'food', 'comida', 'cozinha', 'culinária',
            'prato', 'dish', 'cooking', 'bolo', 'cake', 'torta', 'doce',
            'salgado', 'massa', 'ingrediente', 'preparo', 'modo de fazer'
        ]
        
        text = f"{content.raw_title} {content.raw_caption}".lower()
        
        return any(keyword in text for keyword in recipe_keywords)
    
    async def _fetch_mock_content(self) -> List[RawSocialContent]:
        """Gera dados mock"""
        self.logger.info("Gerando conteúdo MOCK para RSS")
        
        mock_data = []
        num_items = random.randint(2, 5)
        
        for i in range(num_items):
            views = random.randint(5000, 500000)
            likes = int(views * random.uniform(0.02, 0.08))
            shares = int(views * random.uniform(0.005, 0.02))
            comments = int(views * random.uniform(0.01, 0.03))
            
            content = RawSocialContent(
                source_type=SourceType.RSS,
                source_url=f"https://example-blog.com/receita-{i+1}",
                source_profile=f"Blog Culinário {i+1}",
                raw_title=f"Receita Viral: Bolo Delicioso {i+1}",
                raw_caption=f"Aprenda a fazer esta receita incrível que está fazendo sucesso! "
                            f"Ingredientes simples e preparo rápido. #receita #bolo #facil",
                media_url=f"https://example-blog.com/images/recipe-{i+1}.jpg",
                published_at=datetime.utcnow() - timedelta(hours=random.randint(2, 24)),
                views=views,
                likes=likes,
                shares=shares,
                comments=comments,
                hashtags=['receita', 'bolo', 'facil'],
                mentions=[]
            )
            mock_data.append(content)
        
        return mock_data
    
    def _get_relevant_hashtags(self) -> List[str]:
        """RSS não usa hashtags para busca"""
        return []
    
    async def close(self):
        """Fecha a sessão HTTP"""
        if self.session and not self.session.closed:
            await self.session.close()
