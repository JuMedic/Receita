"""
Processador de Receitas - transforma conteúdo viral em receitas padronizadas.
"""
import re
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from loguru import logger

from src.models import (
    Recipe, ViralSignal, Ingredient, NutritionEstimate,
    SocialShort, PublishRecommendation, Meta, Audit,
    Source, Media, TrendMetrics, Category, Difficulty, Priority,
    MediaType, MediaLicense
)
from src.utils.helpers import (
    generate_slug, calculate_fingerprint, clean_text,
    truncate_text, extract_numbers, convert_to_grams,
    format_timestamp
)
from config.settings import config


class RecipeProcessor:
    """Processa e transforma sinais virais em receitas estruturadas"""
    
    def __init__(self):
        self.logger = logger.bind(processor="RecipeProcessor")
        self.processor_id = "viral-recipe-processor-v1"
    
    async def process_viral_signal(self, signal: ViralSignal) -> Optional[Recipe]:
        """
        Processa um sinal viral e retorna uma receita estruturada.
        Retorna None se não conseguir processar.
        """
        try:
            self.logger.info(f"Processando: {signal.content.source_profile} - {signal.content.raw_title}")
            
            # 1. Extrair informações básicas
            extracted_data = await self._extract_recipe_data(signal)
            
            if not extracted_data:
                self.logger.warning("Não foi possível extrair dados suficientes")
                return None
            
            # 2. Validar requisitos mínimos
            if not self._validate_minimum_requirements(extracted_data):
                self.logger.warning("Requisitos mínimos não atendidos")
                return None
            
            # 3. Reescrever e enriquecer
            enriched_data = await self._rewrite_and_enrich(extracted_data, signal)
            
            # 4. Gerar metadados
            metadata = self._generate_metadata(enriched_data)
            
            # 5. Calcular fingerprint
            fingerprint = self._calculate_fingerprint(enriched_data)
            
            # 6. Construir objeto Recipe
            recipe = self._build_recipe(
                signal=signal,
                data=enriched_data,
                metadata=metadata,
                fingerprint=fingerprint
            )
            
            self.logger.info(f"✓ Receita processada: {recipe.title}")
            return recipe
            
        except Exception as e:
            self.logger.error(f"Erro ao processar sinal: {e}", exc_info=True)
            return None
    
    async def _extract_recipe_data(self, signal: ViralSignal) -> Optional[Dict]:
        """
        Extrai dados da receita do conteúdo bruto.
        Em produção, usar LLM/NLP para extração inteligente.
        """
        content = signal.content
        
        # Texto completo
        full_text = f"{content.raw_title or ''}\n{content.raw_caption or ''}"
        
        if not full_text.strip():
            return None
        
        # Simular extração (em produção usar LLM)
        extracted = {
            'raw_text': full_text,
            'title': content.raw_title or self._extract_title(full_text),
            'ingredients': self._extract_ingredients(full_text),
            'instructions': self._extract_instructions(full_text),
            'prep_time': self._extract_time(full_text, 'prep'),
            'cook_time': self._extract_time(full_text, 'cook'),
            'servings': self._extract_servings(full_text),
            'difficulty': self._infer_difficulty(full_text),
            'category': self._infer_category(full_text),
            'tips': self._extract_tips(full_text),
        }
        
        return extracted
    
    def _extract_title(self, text: str) -> str:
        """Extrai ou gera título da receita"""
        # Pegar primeira linha ou primeiras palavras
        lines = text.strip().split('\n')
        title = lines[0] if lines else "Receita Viral"
        
        # Limpar
        title = clean_text(title)
        title = re.sub(r'^(receita|recipe):\s*', '', title, flags=re.IGNORECASE)
        
        return truncate_text(title, 100)
    
    def _extract_ingredients(self, text: str) -> List[Dict[str, str]]:
        """
        Extrai ingredientes do texto.
        Em produção, usar NER (Named Entity Recognition) ou LLM.
        """
        ingredients = []
        
        # Procurar seção de ingredientes
        ingredients_section = re.search(
            r'(?:ingredientes?|ingredients?)[\s:]*\n(.*?)(?:\n\n|modo de|instructions?|preparo)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        
        if ingredients_section:
            section_text = ingredients_section.group(1)
            lines = [line.strip() for line in section_text.split('\n') if line.strip()]
            
            for line in lines[:15]:  # Limitar a 15 ingredientes
                # Tentar parse: "quantidade unidade ingrediente"
                match = re.match(r'^[\-\*•]?\s*(\d+[\.,]?\d*)\s*(\w+)\s+(?:de\s+)?(.+)$', line, re.IGNORECASE)
                
                if match:
                    quantity, unit, name = match.groups()
                    ingredients.append({
                        'name': name.strip(),
                        'quantity': quantity.replace(',', '.'),
                        'unit': unit.lower()
                    })
                else:
                    # Fallback: apenas nome do ingrediente
                    name = re.sub(r'^[\-\*•]\s*', '', line)
                    if len(name) > 3:
                        ingredients.append({
                            'name': name.strip(),
                            'quantity': 'a gosto',
                            'unit': ''
                        })
        
        # Se não encontrou nada, retornar placeholder
        if not ingredients:
            ingredients = [
                {'name': 'Ingredientes não especificados', 'quantity': '', 'unit': ''}
            ]
        
        return ingredients
    
    def _extract_instructions(self, text: str) -> List[str]:
        """
        Extrai instruções/modo de preparo.
        Em produção, usar LLM para melhor extração.
        """
        # Procurar seção de preparo
        instructions_section = re.search(
            r'(?:modo de preparo|instructions?|preparo|como fazer)[\s:]*\n(.*?)(?:\n\n|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        
        if instructions_section:
            section_text = instructions_section.group(1)
            lines = [line.strip() for line in section_text.split('\n') if line.strip()]
            
            # Remover bullets
            instructions = []
            for line in lines[:20]:  # Máximo 20 passos
                line = re.sub(r'^[\d\.\-\*•]\s*', '', line)
                if len(line) > 10:
                    instructions.append(line)
            
            if instructions:
                return instructions
        
        # Fallback
        return [
            "Siga as instruções do vídeo original.",
            "Preparar conforme demonstrado no conteúdo viral."
        ]
    
    def _extract_time(self, text: str, time_type: str) -> int:
        """Extrai tempo de preparo ou cozimento (em minutos)"""
        patterns = {
            'prep': r'(?:preparo|prep\s+time)[\s:]*(\d+)\s*(?:min|minutos?|minutes?)',
            'cook': r'(?:cozimento|cook\s+time|forno)[\s:]*(\d+)\s*(?:min|minutos?|minutes?)'
        }
        
        pattern = patterns.get(time_type, patterns['prep'])
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return int(match.group(1))
        
        # Valores padrão
        return 15 if time_type == 'prep' else 20
    
    def _extract_servings(self, text: str) -> str:
        """Extrai rendimento/porções"""
        match = re.search(
            r'(?:rende|serve|porções?|servings?)[\s:]*(\d+)\s*(?:porções?|pessoas?|servings?)?',
            text,
            re.IGNORECASE
        )
        
        if match:
            num = match.group(1)
            return f"{num} porções"
        
        return "4 porções"  # Padrão
    
    def _infer_difficulty(self, text: str) -> Difficulty:
        """Infere dificuldade baseado em keywords e complexidade"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['fácil', 'easy', 'simples', 'rápid']):
            return Difficulty.FACIL
        
        if any(word in text_lower for word in ['difícil', 'complexo', 'advanced']):
            return Difficulty.DIFICIL
        
        return Difficulty.MEDIO
    
    def _infer_category(self, text: str) -> Category:
        """Infere categoria baseado em keywords"""
        text_lower = text.lower()
        
        categories_map = {
            Category.DOCES: ['bolo', 'torta', 'doce', 'chocolate', 'sobremesa', 'cake', 'dessert'],
            Category.SALGADOS: ['salgado', 'pão', 'pizza', 'savory'],
            Category.BEBIDAS: ['suco', 'bebida', 'drink', 'smoothie', 'café'],
            Category.VEGANA: ['vegan', 'vegano', 'sem carne'],
            Category.FITNESS: ['fit', 'fitness', 'saudável', 'healthy', 'proteína'],
            Category.RAPIDAS: ['rápido', 'quick', 'fácil', '5 minutos', 'express'],
        }
        
        for category, keywords in categories_map.items():
            if any(word in text_lower for word in keywords):
                return category
        
        return Category.SALGADOS  # Padrão
    
    def _extract_tips(self, text: str) -> Optional[str]:
        """Extrai dicas ou observações"""
        tip_patterns = [
            r'(?:dica|tip|obs|observação)[\s:]*(.+?)(?:\n|$)',
            r'(?:pode|você pode|variação)[\s:]*(.+?)(?:\n|$)'
        ]
        
        for pattern in tip_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                tip = clean_text(match.group(1))
                if len(tip) > 10:
                    return truncate_text(tip, 200)
        
        return None
    
    def _validate_minimum_requirements(self, data: Dict) -> bool:
        """Valida se dados atendem requisitos mínimos"""
        if not data.get('title'):
            return False
        
        if not data.get('ingredients') or len(data['ingredients']) < config.MIN_INGREDIENTS:
            self.logger.warning(f"Poucos ingredientes: {len(data.get('ingredients', []))}")
            return False
        
        if not data.get('instructions') or len(data['instructions']) < config.MIN_INSTRUCTIONS:
            self.logger.warning(f"Poucas instruções: {len(data.get('instructions', []))}")
            return False
        
        return True
    
    async def _rewrite_and_enrich(self, data: Dict, signal: ViralSignal) -> Dict:
        """
        Reescreve conteúdo de forma original e enriquece com informações adicionais.
        Em produção, usar LLM (GPT-4, Claude) para reescrita profissional.
        """
        # Reescrever título (SEO-friendly)
        original_title = data['title']
        rewritten_title = await self._rewrite_title(original_title, data)
        
        # Gerar resumo SEO
        summary = await self._generate_summary(data, signal)
        
        # Normalizar ingredientes
        normalized_ingredients = self._normalize_ingredients(data['ingredients'])
        
        # Enriquecer instruções
        enriched_instructions = self._enrich_instructions(data['instructions'])
        
        # Gerar conteúdo social
        social_content = self._generate_social_content(rewritten_title, data)
        
        # Estimar nutrição e custo
        nutrition = self._estimate_nutrition(normalized_ingredients)
        cost = self._estimate_cost(normalized_ingredients)
        
        # Gerar prompt de imagem
        image_prompt = self._generate_image_prompt(rewritten_title, data)
        
        return {
            **data,
            'title': rewritten_title,
            'summary': summary,
            'ingredients': normalized_ingredients,
            'instructions': enriched_instructions,
            'social_content': social_content,
            'nutrition': nutrition,
            'cost': cost,
            'image_prompt': image_prompt
        }
    
    async def _rewrite_title(self, original: str, data: Dict) -> str:
        """
        Reescreve título de forma atraente e SEO-friendly.
        Em produção, usar LLM.
        """
        # Simplificação: adicionar adjetivos e otimizar
        title = clean_text(original)
        
        # Remover hashtags
        title = re.sub(r'#\w+', '', title).strip()
        
        # Adicionar contexto se muito curto
        if len(title.split()) < 4:
            category = data.get('category', Category.RAPIDAS).value
            title = f"{title} - {category}"
        
        return truncate_text(title, 120)
    
    async def _generate_summary(self, data: Dict, signal: ViralSignal) -> str:
        """Gera resumo SEO da receita"""
        title = data['title']
        difficulty = data['difficulty'].value
        total_time = data['prep_time'] + data['cook_time']
        views = signal.content.views
        
        summary = (
            f"{title}. Receita {difficulty.lower()}, pronta em {total_time} minutos. "
            f"Viral com {self._format_number(views)} visualizações!"
        )
        
        return truncate_text(summary, 150)
    
    def _normalize_ingredients(self, ingredients: List[Dict]) -> List[Ingredient]:
        """
        Normaliza e padroniza ingredientes.
        Converte medidas quando possível.
        """
        normalized = []
        
        for ing in ingredients:
            # Normalizar unidades
            unit = ing.get('unit', '').lower()
            quantity = ing.get('quantity', '')
            name = ing.get('name', '')
            
            # Conversões comuns
            if unit in ['xícara', 'xicara', 'cup']:
                if 'farinha' in name.lower() or 'açúcar' in name.lower():
                    unit = 'g'
                    if quantity.replace('.', '').isdigit():
                        quantity = str(int(float(quantity) * 120))
            
            # Criar ingrediente
            ingredient = Ingredient(
                name=clean_text(name),
                quantity=str(quantity),
                unit=unit
            )
            normalized.append(ingredient)
        
        return normalized
    
    def _enrich_instructions(self, instructions: List[str]) -> List[str]:
        """Enriquece instruções tornando-as mais claras"""
        enriched = []
        
        for i, instruction in enumerate(instructions, 1):
            # Adicionar número se não tiver
            if not instruction[0].isdigit():
                instruction = f"{i}. {instruction}"
            
            # Capitalizar primeira letra
            instruction = instruction[0].upper() + instruction[1:]
            
            # Garantir ponto final
            if not instruction.endswith('.'):
                instruction += '.'
            
            enriched.append(instruction)
        
        return enriched
    
    def _generate_social_content(self, title: str, data: Dict) -> SocialShort:
        """Gera conteúdo para redes sociais"""
        # Caption para TikTok (curta)
        tiktok_caption = f"{title[:50]}... 🔥 Faz e me marca! #receita #tiktokfood #viral"
        
        # Caption para Instagram (mais longa)
        instagram_caption = (
            f"{title} 😍\n\n"
            f"✨ Receita viral que você precisa tentar!\n"
            f"Salva para fazer depois 📌\n\n"
            f"#receitas #reels #comida #food #viral"
        )
        
        # Script para Short/Reel
        short_script = (
            "1) Mostre o prato finalizado bem de perto; "
            "2) Exiba os ingredientes principais; "
            "3) Faça call-to-action: 'Marca quem precisa fazer isso!'"
        )
        
        return SocialShort(
            tiktok_caption=truncate_text(tiktok_caption, 300),
            instagram_caption=truncate_text(instagram_caption, 2200),
            short_script=short_script
        )
    
    def _estimate_nutrition(self, ingredients: List[Ingredient]) -> Optional[NutritionEstimate]:
        """
        Estima valores nutricionais básicos.
        Em produção, usar API de nutrição (USDA, Nutritionix) ou LLM.
        """
        # Simplificação: estimativas genéricas baseadas em ingredientes comuns
        calories = 0
        fat = 0.0
        carb = 0.0
        protein = 0.0
        
        for ing in ingredients:
            name = ing.name.lower()
            
            # Estimativas muito simplificadas
            if 'farinha' in name or 'açúcar' in name:
                calories += 200
                carb += 50
            elif 'ovo' in name:
                calories += 70
                protein += 6
                fat += 5
            elif 'manteiga' in name or 'óleo' in name:
                calories += 100
                fat += 10
            elif 'leite' in name:
                calories += 60
                carb += 5
                protein += 3
        
        if calories == 0:
            return None
        
        return NutritionEstimate(
            calories=int(calories / 4),  # Por porção (assumindo 4 porções)
            fat_g=round(fat, 1),
            carb_g=round(carb, 1),
            protein_g=round(protein, 1)
        )
    
    def _estimate_cost(self, ingredients: List[Ingredient]) -> str:
        """Estima custo da receita"""
        # Simplificação: baseado no número de ingredientes
        num_ingredients = len(ingredients)
        
        if num_ingredients <= 5:
            return "R$8-15"
        elif num_ingredients <= 10:
            return "R$15-30"
        else:
            return "R$30-50"
    
    def _generate_image_prompt(self, title: str, data: Dict) -> str:
        """Gera prompt para geração de imagem via IA"""
        category = data.get('category', Category.RAPIDAS).value
        
        prompt = (
            f"Foto profissional 16:9 de {title.lower()}, "
            f"estilo food photography, iluminação natural suave, "
            f"close-up do prato, cores vibrantes, fundo desfocado, "
            f"composição apetitosa, {category.lower()}"
        )
        
        return truncate_text(prompt, 300)
    
    def _generate_metadata(self, data: Dict) -> Meta:
        """Gera metadados SEO"""
        title = data['title']
        
        seo_title = truncate_text(title, 60)
        meta_description = data['summary']
        
        return Meta(
            seo_title=seo_title,
            meta_description=truncate_text(meta_description, 150),
            duplicate=False
        )
    
    def _calculate_fingerprint(self, data: Dict) -> str:
        """Calcula fingerprint para deduplicação"""
        ingredient_names = [ing.name for ing in data['ingredients']]
        return calculate_fingerprint(ingredient_names, data['title'])
    
    def _build_recipe(
        self,
        signal: ViralSignal,
        data: Dict,
        metadata: Meta,
        fingerprint: str
    ) -> Recipe:
        """Constrói objeto Recipe completo"""
        content = signal.content
        
        # Source
        source = Source(
            type=content.source_type,
            profile=content.source_profile,
            name=content.source_profile,
            url=content.source_url
        )
        
        # Media
        media = Media(
            media_type=MediaType.VIDEO if 'video' in content.media_url else MediaType.IMAGE,
            media_url=content.media_url or "https://placeholder.com/recipe.jpg",
            thumbnail_frame_time=f"{config.THUMBNAIL_FRAME_TIME}s",
            media_license=MediaLicense.PUBLIC
        )
        
        # Trend Metrics
        trend_metrics = TrendMetrics(
            views=content.views,
            likes=content.likes,
            shares=content.shares,
            growth_rate_percent=signal.growth_rate,
            time_window_hours=signal.time_window_hours
        )
        
        # Tags
        tags = list(set(content.hashtags[:10]))  # Máximo 10, único
        
        # Publish Recommendation
        priority = Priority.VIRAL if signal.viral_score >= 0.8 else Priority.NORMAL
        publish = config.AUTO_MODE and signal.is_viral
        
        publish_recommendation = PublishRecommendation(
            publish=publish,
            priority=priority
        )
        
        # Audit
        audit = Audit(
            created_at=datetime.utcnow(),
            processed_by=self.processor_id,
            confidence_score=signal.viral_score,
            notes=f"Sinais: {', '.join(signal.signals_detected)}"
        )
        
        # Construir Recipe
        recipe = Recipe(
            title=data['title'],
            slug=generate_slug(data['title']),
            summary=data['summary'],
            source=source,
            media=media,
            trend_metrics=trend_metrics,
            category=data['category'],
            tags=tags,
            servings=data['servings'],
            prep_time_minutes=data['prep_time'],
            cook_time_minutes=data['cook_time'],
            total_time_minutes=data['prep_time'] + data['cook_time'],
            difficulty=data['difficulty'],
            estimated_cost=data['cost'],
            ingredients=data['ingredients'],
            instructions=data['instructions'],
            tips=data.get('tips'),
            nutrition_estimate=data.get('nutrition'),
            image_prompt=data.get('image_prompt'),
            social_short=data['social_content'],
            publish_recommendation=publish_recommendation,
            duplicate_fingerprint=fingerprint,
            meta=metadata,
            audit=audit
        )
        
        return recipe
    
    def _format_number(self, num: int) -> str:
        """Formata número para exibição (ex: 1.5M, 150K)"""
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.0f}K"
        return str(num)
