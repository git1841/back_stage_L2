"""
Fonctions utilitaires pour l'application
"""

from datetime import datetime
from typing import Optional, Dict, Any
import os

def format_date(date_obj, format="%Y-%m-%d") -> str:
    """Formate une date"""
    if not date_obj:
        return None
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime(format)

def calculate_percentage(part: int, total: int, decimals: int = 2) -> float:
    """Calcule un pourcentage"""
    if total == 0:
        return 0.0
    return round((part * 100.0) / total, decimals)

def safe_int(value, default=0) -> int:
    """Convertit en int de manière sûre"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0) -> float:
    """Convertit en float de manière sûre"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def clean_string(value: str) -> Optional[str]:
    """Nettoie une chaîne de caractères"""
    if not value:
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None

def normalize_etat(etat: str) -> Optional[str]:
    """Normalise les états des matériels"""
    if not etat:
        return None
    
    etat_lower = etat.lower().strip()
    
    # Mapping des variations
    etat_mapping = {
        'fonctionnel': 'Fonctionnel',
        'fonctionelle': 'Fonctionnel',
        'fonctionne': 'Fonctionnel',
        'ok': 'Fonctionnel',
        'non fonctionnel': 'Non fonctionnel',
        'non fonctionelle': 'Non fonctionnel',
        'en panne': 'Non fonctionnel',
        'panne': 'Non fonctionnel',
        'hs': 'Non fonctionnel',
        'hors service': 'Non fonctionnel'
    }
    
    return etat_mapping.get(etat_lower, etat)

def ensure_directory_exists(directory_path: str):
    """Crée un répertoire s'il n'existe pas"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Répertoire créé: {directory_path}")

def validate_excel_columns(df_columns, required_columns) -> Dict[str, Any]:
    """Valide les colonnes d'un DataFrame Excel"""
    missing = []
    for col in required_columns:
        if col not in df_columns:
            missing.append(col)
    
    if missing:
        return {
            "valid": False,
            "missing_columns": missing,
            "message": f"Colonnes manquantes: {', '.join(missing)}"
        }
    
    return {
        "valid": True,
        "message": "Toutes les colonnes requises sont présentes"
    }

def paginate_query(total: int, skip: int, limit: int) -> Dict[str, Any]:
    """Calcule les métadonnées de pagination"""
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1
    has_next = (skip + limit) < total
    has_previous = skip > 0
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "total_pages": total_pages,
        "current_page": current_page,
        "has_next": has_next,
        "has_previous": has_previous
    }

def sanitize_filename(filename: str) -> str:
    """Nettoie un nom de fichier"""
    import re
    # Supprimer les caractères non-alphanumériques (sauf . - _)
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Remplacer les espaces par des underscores
    filename = re.sub(r'\s+', '_', filename)
    # Limiter la longueur
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    return f"{name}{ext}"

def get_file_size_mb(file_path: str) -> float:
    """Retourne la taille d'un fichier en MB"""
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    return 0.0

def format_number(number: int) -> str:
    """Formate un nombre avec des séparateurs de milliers"""
    return f"{number:,}".replace(',', ' ')

def get_date_range_description(date_ancienne, date_nouvelle) -> str:
    """Génère une description de plage de dates"""
    if not date_ancienne or not date_nouvelle:
        return "Période non définie"
    
    return f"Du {format_date(date_ancienne)} au {format_date(date_nouvelle)}"

def calculate_growth_rate(old_value: int, new_value: int) -> Dict[str, Any]:
    """Calcule le taux de croissance entre deux valeurs"""
    if old_value == 0:
        return {
            "growth": new_value,
            "growth_rate": 0 if new_value == 0 else 100.0,
            "is_positive": new_value > 0
        }
    
    growth = new_value - old_value
    growth_rate = (growth / old_value) * 100
    
    return {
        "growth": growth,
        "growth_rate": round(growth_rate, 2),
        "is_positive": growth > 0
    }

def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Tronque un texte s'il dépasse une longueur maximale"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def group_by_key(items: list, key: str) -> Dict[str, list]:
    """Groupe une liste d'éléments par une clé"""
    grouped = {}
    for item in items:
        key_value = item.get(key)
        if key_value not in grouped:
            grouped[key_value] = []
        grouped[key_value].append(item)
    return grouped

def get_unique_values(items: list, key: str) -> list:
    """Récupère les valeurs uniques d'une clé dans une liste"""
    return list(set(item.get(key) for item in items if item.get(key)))

def merge_dicts(*dicts) -> dict:
    """Fusionne plusieurs dictionnaires"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result

class Timer:
    """Context manager pour mesurer le temps d'exécution"""
    def __init__(self, description="Operation"):
        self.description = description
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, *args):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        print(f"{self.description} took {duration:.2f} seconds")
    
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None