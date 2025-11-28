"""
Sistema de deduplicação - detecta receitas duplicadas.
"""
from typing import List, Tuple, Optional
from loguru import logger

from src.models import Recipe
from src.utils.helpers import calculate_similarity
from config.settings import config


class DeduplicationService:
    """Serviço de deduplicação de receitas"""
    
    def __init__(self):
        self.logger = logger.bind(service="Deduplication")
        self.known_fingerprints = set()
        self.recipe_cache = []
    
    def is_duplicate(self, recipe: Recipe, existing_recipes: List[Recipe] = None) -> Tuple[bool, Optional[str]]:
        """
        Verifica se receita é duplicata.
        Retorna (is_duplicate, reason)
        """
        # Verificar fingerprint exato
        if recipe.duplicate_fingerprint in self.known_fingerprints:
            return True, "Fingerprint idêntico encontrado"
        
        # Verificar contra receitas existentes
        if existing_recipes:
            for existing in existing_recipes:
                # Fingerprint match
                if recipe.duplicate_fingerprint == existing.duplicate_fingerprint:
                    return True, f"Duplicata de: {existing.title}"
                
                # Similaridade de título
                title_similarity = calculate_similarity(recipe.title, existing.title)
                if title_similarity > config.DUPLICATE_THRESHOLD:
                    # Verificar se ingredientes também são similares
                    ing_similarity = self._compare_ingredients(recipe, existing)
                    if ing_similarity > config.DUPLICATE_THRESHOLD:
                        return True, f"Similaridade alta com: {existing.title} ({title_similarity:.2f})"
        
        return False, None
    
    def _compare_ingredients(self, recipe1: Recipe, recipe2: Recipe) -> float:
        """Compara similaridade de ingredientes"""
        ing1 = set(ing.name.lower() for ing in recipe1.ingredients)
        ing2 = set(ing.name.lower() for ing in recipe2.ingredients)
        
        if not ing1 or not ing2:
            return 0.0
        
        intersection = ing1.intersection(ing2)
        union = ing1.union(ing2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def mark_as_seen(self, recipe: Recipe):
        """Marca receita como vista"""
        self.known_fingerprints.add(recipe.duplicate_fingerprint)
        self.recipe_cache.append(recipe)
        
        # Limitar cache
        if len(self.recipe_cache) > 1000:
            self.recipe_cache = self.recipe_cache[-500:]
            self.known_fingerprints = {r.duplicate_fingerprint for r in self.recipe_cache}
