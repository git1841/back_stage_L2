"""
Tests unitaires pour les services de l'application
Pour exécuter: pytest tests/test_services.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date
import pandas as pd

# Import des services à tester
import sys
sys.path.insert(0, '..')
from services.auth_service import AuthService
from services.statistics_service import StatisticsService
from utils.helpers import (
    calculate_percentage,
    normalize_etat,
    paginate_query,
    calculate_growth_rate
)

class TestHelpers:
    """Tests pour les fonctions utilitaires"""
    
    def test_calculate_percentage(self):
        """Test du calcul de pourcentage"""
        assert calculate_percentage(50, 100) == 50.0
        assert calculate_percentage(1, 3, decimals=2) == 33.33
        assert calculate_percentage(0, 0) == 0.0
        assert calculate_percentage(75, 150) == 50.0
    
    def test_normalize_etat(self):
        """Test de normalisation des états"""
        assert normalize_etat("fonctionnel") == "Fonctionnel"
        assert normalize_etat("FONCTIONNEL") == "Fonctionnel"
        assert normalize_etat("non fonctionnel") == "Non fonctionnel"
        assert normalize_etat("en panne") == "Non fonctionnel"
        assert normalize_etat("hs") == "Non fonctionnel"
        assert normalize_etat(None) is None
        assert normalize_etat("") is None
    
    def test_paginate_query(self):
        """Test des métadonnées de pagination"""
        result = paginate_query(total=100, skip=0, limit=10)
        assert result['total'] == 100
        assert result['total_pages'] == 10
        assert result['current_page'] == 1
        assert result['has_next'] is True
        assert result['has_previous'] is False
        
        result = paginate_query(total=100, skip=90, limit=10)
        assert result['current_page'] == 10
        assert result['has_next'] is False
        assert result['has_previous'] is True
    
    def test_calculate_growth_rate(self):
        """Test du calcul de taux de croissance"""
        result = calculate_growth_rate(100, 120)
        assert result['growth'] == 20
        assert result['growth_rate'] == 20.0
        assert result['is_positive'] is True
        
        result = calculate_growth_rate(100, 80)
        assert result['growth'] == -20
        assert result['growth_rate'] == -20.0
        assert result['is_positive'] is False
        
        result = calculate_growth_rate(0, 50)
        assert result['growth'] == 50
        assert result['is_positive'] is True

class TestAuthService:
    """Tests pour le service d'authentification"""
    
    @patch('services.auth_service.execute_query')
    @patch('services.auth_service.hash_password')
    def test_register_user_success(self, mock_hash, mock_query):
        """Test d'inscription réussie"""
        mock_query.side_effect = [
            None,  # Utilisateur n'existe pas
            1,     # ID du nouvel utilisateur
            {      # Utilisateur créé
                'id': 1,
                'mail': 'test@example.com',
                'created_at': date.today()
            }
        ]
        mock_hash.return_value = "hashed_password"
        
        result = AuthService.register_user("test@example.com", "password123")
        
        assert result['id'] == 1
        assert result['mail'] == 'test@example.com'
        mock_hash.assert_called_once_with("password123")
    
    @patch('services.auth_service.execute_query')
    def test_register_user_duplicate_email(self, mock_query):
        """Test d'inscription avec email existant"""
        mock_query.return_value = {'id': 1}  # Utilisateur existe déjà
        
        with pytest.raises(Exception):  # Devrait lever une HTTPException
            AuthService.register_user("existing@example.com", "password123")

class TestStatisticsService:
    """Tests pour le service de statistiques"""
    
    @patch('services.statistics_service.execute_query')
    def test_calculate_materiel_changes_first_import(self, mock_query):
        """Test calcul nouveaux matériels pour première importation"""
        mock_query.side_effect = [
            None,  # Pas de date précédente
            {'total': 100}  # Total matériels
        ]
        
        nouveau, perdu = StatisticsService._calculate_materiel_changes(1)
        
        assert nouveau == 100
        assert perdu == 0
    
    @patch('services.statistics_service.execute_query')
    def test_calculate_materiel_changes_growth(self, mock_query):
        """Test calcul avec croissance"""
        mock_query.side_effect = [
            {'id_date': 1},  # Date précédente existe
            {'total': 120},  # Total actuel
            {'total': 100}   # Total précédent
        ]
        
        nouveau, perdu = StatisticsService._calculate_materiel_changes(2)
        
        assert nouveau == 20
        assert perdu == 0
    
    @patch('services.statistics_service.execute_query')
    def test_calculate_materiel_changes_loss(self, mock_query):
        """Test calcul avec perte"""
        mock_query.side_effect = [
            {'id_date': 1},  # Date précédente existe
            {'total': 80},   # Total actuel
            {'total': 100}   # Total précédent
        ]
        
        nouveau, perdu = StatisticsService._calculate_materiel_changes(2)
        
        assert nouveau == 0
        assert perdu == 20

class TestExcelProcessing:
    """Tests pour le traitement de fichiers Excel"""
    
    def test_excel_column_inheritance(self):
        """Test de l'héritage des valeurs dans les colonnes"""
        data = {
            'code': ['630601', None, None],
            'region': ['ATSIMO ANDREFANA', None, None],
            'nom_materiel': ['Imprimante 1', 'Imprimante 2', 'Imprimante 3']
        }
        df = pd.DataFrame(data)
        
        # Simuler l'héritage
        df['code'] = df['code'].fillna(method='ffill')
        df['region'] = df['region'].fillna(method='ffill')
        
        assert df.iloc[1]['code'] == '630601'
        assert df.iloc[2]['code'] == '630601'
        assert df.iloc[1]['region'] == 'ATSIMO ANDREFANA'
        assert df.iloc[2]['region'] == 'ATSIMO ANDREFANA'
    
    def test_empty_values_to_none(self):
        """Test conversion valeurs vides en None"""
        data = {
            'nom_materiel': ['Imprimante', '', None, '  '],
            'etat': ['Fonctionnel', '', None, 'Non fonctionnel']
        }
        df = pd.DataFrame(data)
        df = df.where(pd.notna(df), None)
        
        # Remplacer les chaînes vides
        df = df.replace('', None)
        df = df.replace('  ', None)
        
        assert df.iloc[1]['nom_materiel'] is None
        assert df.iloc[2]['nom_materiel'] is None
        assert df.iloc[1]['etat'] is None

class TestPagination:
    """Tests pour la pagination"""
    
    def test_pagination_first_page(self):
        """Test première page"""
        meta = paginate_query(100, 0, 10)
        assert meta['current_page'] == 1
        assert meta['has_previous'] is False
        assert meta['has_next'] is True
    
    def test_pagination_middle_page(self):
        """Test page du milieu"""
        meta = paginate_query(100, 50, 10)
        assert meta['current_page'] == 6
        assert meta['has_previous'] is True
        assert meta['has_next'] is True
    
    def test_pagination_last_page(self):
        """Test dernière page"""
        meta = paginate_query(100, 90, 10)
        assert meta['current_page'] == 10
        assert meta['has_previous'] is True
        assert meta['has_next'] is False
    
    def test_pagination_partial_last_page(self):
        """Test dernière page partielle"""
        meta = paginate_query(95, 90, 10)
        assert meta['total_pages'] == 10
        assert meta['current_page'] == 10

@pytest.fixture
def mock_db_connection():
    """Fixture pour simuler une connexion à la base de données"""
    with patch('config.database.Database.get_connection') as mock:
        connection = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = {'id': 1}
        cursor.fetchall.return_value = [{'id': 1}, {'id': 2}]
        connection.cursor.return_value = cursor
        mock.return_value = connection
        yield connection

class TestDatabaseOperations:
    """Tests pour les opérations de base de données"""
    
    def test_connection_context_manager(self, mock_db_connection):
        """Test du context manager pour les connexions"""
        from config.database import Database
        
        with Database.get_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchone()
        
        assert result['id'] == 1
        mock_db_connection.cursor.assert_called_once()

# Configuration pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])