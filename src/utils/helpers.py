"""
Utilitários gerais do sistema.
"""
import hashlib
import re
from typing import Dict, List, Any
from datetime import datetime, timezone
from slugify import slugify as make_slug
import unicodedata


def generate_slug(text: str) -> str:
    """Gera slug otimizado para URLs"""
    return make_slug(text, max_length=150, word_boundary=True, separator='-')


def normalize_text(text: str) -> str:
    """Normaliza texto removendo acentos e caracteres especiais"""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])


def calculate_fingerprint(ingredients: List[str], title: str) -> str:
    """
    Calcula fingerprint único para deduplicação.
    Baseado em ingredientes normalizados + título normalizado.
    """
    # Normalizar e ordenar ingredientes
    normalized_ingredients = sorted([
        normalize_text(ing.lower().strip())
        for ing in ingredients
    ])
    
    # Normalizar título
    normalized_title = normalize_text(title.lower().strip())
    
    # Criar string combinada
    combined = f"{normalized_title}::{':'.join(normalized_ingredients)}"
    
    # Gerar hash SHA256
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()


def extract_hashtags(text: str) -> List[str]:
    """Extrai hashtags de um texto"""
    if not text:
        return []
    return re.findall(r'#(\w+)', text)


def extract_mentions(text: str) -> List[str]:
    """Extrai menções (@usuario) de um texto"""
    if not text:
        return []
    return re.findall(r'@(\w+)', text)


def clean_text(text: str) -> str:
    """
    Limpa texto removendo emojis, caracteres especiais excessivos,
    mas mantendo pontuação básica.
    """
    if not text:
        return ""
    
    # Remover emojis
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # símbolos & pictogramas
        u"\U0001F680-\U0001F6FF"  # transporte & símbolos de mapa
        u"\U0001F1E0-\U0001F1FF"  # bandeiras (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub(r'', text)
    
    # Remover múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def format_timestamp(dt: datetime = None) -> str:
    """Formata timestamp no formato ISO 8601"""
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time_to_seconds(time_str: str) -> int:
    """
    Converte string de tempo para segundos.
    Exemplos: '12s', '1m30s', '1h5m', '90'
    """
    if not time_str:
        return 0
    
    time_str = time_str.lower().strip()
    
    # Se for apenas número, assume segundos
    if time_str.isdigit():
        return int(time_str)
    
    total_seconds = 0
    
    # Horas
    hours_match = re.search(r'(\d+)h', time_str)
    if hours_match:
        total_seconds += int(hours_match.group(1)) * 3600
    
    # Minutos
    minutes_match = re.search(r'(\d+)m', time_str)
    if minutes_match:
        total_seconds += int(minutes_match.group(1)) * 60
    
    # Segundos
    seconds_match = re.search(r'(\d+)s', time_str)
    if seconds_match:
        total_seconds += int(seconds_match.group(1))
    
    return total_seconds


def format_cost_range(min_cost: float, max_cost: float, currency: str = "R$") -> str:
    """Formata faixa de custo"""
    return f"{currency}{int(min_cost)}-{int(max_cost)}"


def sanitize_filename(filename: str) -> str:
    """Sanitiza nome de arquivo removendo caracteres inválidos"""
    # Remover caracteres inválidos
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Limitar tamanho
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    return filename


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calcula similaridade simples entre dois textos (0.0 a 1.0).
    Usa método Jaccard com n-grams.
    """
    def get_ngrams(text: str, n: int = 3) -> set:
        text = normalize_text(text.lower())
        return set(text[i:i+n] for i in range(len(text) - n + 1))
    
    ngrams1 = get_ngrams(text1)
    ngrams2 = get_ngrams(text2)
    
    if not ngrams1 or not ngrams2:
        return 0.0
    
    intersection = ngrams1.intersection(ngrams2)
    union = ngrams1.union(ngrams2)
    
    return len(intersection) / len(union) if union else 0.0


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Trunca texto adicionando sufixo se necessário"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rstrip() + suffix


def extract_numbers(text: str) -> List[float]:
    """Extrai todos os números de um texto"""
    return [float(n) for n in re.findall(r'\d+\.?\d*', text)]


def convert_to_grams(quantity: float, unit: str) -> float:
    """
    Converte unidades comuns para gramas.
    Retorna None se unidade desconhecida.
    """
    unit = unit.lower().strip()
    
    conversions = {
        'kg': 1000,
        'g': 1,
        'mg': 0.001,
        'lb': 453.592,
        'oz': 28.3495,
        'xícara': 240,  # aproximado para líquidos
        'xicara': 240,
        'colher de sopa': 15,
        'colher sopa': 15,
        'cs': 15,
        'colher de chá': 5,
        'colher cha': 5,
        'cc': 5,
        'l': 1000,  # litro (assume água)
        'ml': 1,
        'dl': 100,
    }
    
    return quantity * conversions.get(unit, None)


def validate_url(url: str) -> bool:
    """Valida se string é URL válida"""
    url_pattern = re.compile(
        r'^https?://'  # http:// ou https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domínio
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # porta opcional
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return url_pattern.match(url) is not None


def batch_items(items: List[Any], batch_size: int) -> List[List[Any]]:
    """Divide lista em batches de tamanho específico"""
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Mescla dois dicionários recursivamente"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result
