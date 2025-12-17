"""
Script de test pour l'API Gestion Matériels
Ce script teste tous les endpoints principaux de l'API
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "mail": f"test_{datetime.now().timestamp()}@example.com",
    "mot_de_passe": "Test123456"
}

# Variables globales
token = None
headers = {}
id_date_import = None

def print_section(title):
    """Affiche une section"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_response(response, show_json=True):
    """Affiche la réponse"""
    print(f"Status: {response.status_code}")
    if show_json and response.status_code < 500:
        try:
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"Response: {response.text}")
    print()

def test_health():
    """Test du health check"""
    print_section("1. HEALTH CHECK")
    
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    
    assert response.status_code == 200, "Health check failed"
    print("✓ Health check OK")

def test_register():
    """Test de l'inscription"""
    print_section("2. INSCRIPTION")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=TEST_USER
    )
    print_response(response)
    
    assert response.status_code == 201, "Registration failed"
    print("✓ Inscription réussie")

def test_login():
    """Test de la connexion"""
    global token, headers
    print_section("3. CONNEXION")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=TEST_USER
    )
    print_response(response)
    
    assert response.status_code == 200, "Login failed"
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✓ Connexion réussie - Token: {token[:50]}...")

def test_me():
    """Test récupération infos utilisateur"""
    print_section("4. INFORMATIONS UTILISATEUR")
    
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200, "Get user info failed"
    print("✓ Récupération des infos utilisateur OK")

def test_get_dates():
    """Test récupération des dates d'importation"""
    global id_date_import
    print_section("5. DATES D'IMPORTATION")
    
    response = requests.get(
        f"{BASE_URL}/upload/dates",
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200, "Get dates failed"
    dates = response.json()
    if dates['total'] > 0:
        id_date_import = dates['dates'][0]['id_date']
        print(f"✓ {dates['total']} dates trouvées - Utilisation de id_date: {id_date_import}")
    else:
        print("⚠ Aucune date d'importation trouvée (normal si aucun fichier n'a été uploadé)")

def test_statistics():
    """Test des statistiques"""
    print_section("6. STATISTIQUES")
    
    if not id_date_import:
        print("⚠ Pas de date d'importation disponible - Test skippé")
        return
    
    response = requests.get(
        f"{BASE_URL}/statistics/",
        params={
            "id_date_import": id_date_import,
            "skip_type": 0,
            "limit_type": 5,
            "skip_region": 0,
            "limit_region": 5
        },
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200, "Get statistics failed"
    stats = response.json()
    print(f"✓ Statistiques récupérées:")
    print(f"  - Nouveaux matériels: {stats['nouveau_materiel']}")
    print(f"  - Matériels perdus: {stats['materiel_perdu']}")
    print(f"  - Total matériels: {stats['resume_global']['total_materiels']}")

def test_dashboard():
    """Test du dashboard"""
    print_section("7. DASHBOARD")
    
    response = requests.get(
        f"{BASE_URL}/statistics/dashboard",
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200, "Get dashboard failed"
    
    if response.json().get('statistics'):
        print("✓ Dashboard récupéré avec succès")
    else:
        print("⚠ Dashboard vide (normal si aucun fichier uploadé)")

def test_materiels_list():
    """Test de la liste des matériels"""
    print_section("8. LISTE DES MATÉRIELS")
    
    if not id_date_import:
        print("⚠ Pas de date d'importation disponible - Test skippé")
        return
    
    response = requests.get(
        f"{BASE_URL}/materiels/all",
        params={
            "id_date_import": id_date_import,
            "skip": 0,
            "limit": 5
        },
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200, "Get materiels failed"
    result = response.json()
    print(f"✓ Liste des matériels récupérée:")
    print(f"  - Total: {result['total']}")
    print(f"  - Affichés: {len(result['data'])}")

def test_search_by_code():
    """Test de recherche par code"""
    print_section("9. RECHERCHE PAR CODE")
    
    if not id_date_import:
        print("⚠ Pas de date d'importation disponible - Test skippé")
        return
    
    # Essayer avec le code 630601 de l'exemple
    response = requests.get(
        f"{BASE_URL}/materiels/search/by-code",
        params={
            "code": "630601",
            "id_date_import": id_date_import,
            "skip": 0,
            "limit": 5
        },
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200, "Search by code failed"
    result = response.json()
    print(f"✓ Recherche par code effectuée:")
    print(f"  - Code: {result['code']}")
    print(f"  - Résultats trouvés: {result['total']}")

def test_upload_history():
    """Test de l'historique des uploads"""
    print_section("10. HISTORIQUE DES UPLOADS")
    
    response = requests.get(
        f"{BASE_URL}/upload/history",
        params={
            "skip": 0,
            "limit": 10
        },
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200, "Get upload history failed"
    result = response.json()
    print(f"✓ Historique récupéré:")
    print(f"  - Total uploads: {result['total']}")

def test_change_password():
    """Test changement de mot de passe"""
    print_section("11. CHANGEMENT DE MOT DE PASSE")
    
    new_password = "NewTest123456"
    
    # Changer le mot de passe
    response = requests.post(
        f"{BASE_URL}/auth/change-password",
        json={
            "ancien_mot_de_passe": TEST_USER['mot_de_passe'],
            "nouveau_mot_de_passe": new_password
        },
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200, "Change password failed"
    print("✓ Mot de passe changé")
    
    # Tester la connexion avec le nouveau mot de passe
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "mail": TEST_USER['mail'],
            "mot_de_passe": new_password
        }
    )
    
    assert response.status_code == 200, "Login with new password failed"
    print("✓ Connexion avec nouveau mot de passe réussie")
    
    # Remettre l'ancien mot de passe pour les tests suivants
    TEST_USER['mot_de_passe'] = new_password

def test_unauthorized_access():
    """Test d'accès non autorisé"""
    print_section("12. TEST ACCÈS NON AUTORISÉ")
    
    # Essayer d'accéder sans token
    response = requests.get(f"{BASE_URL}/auth/me")
    print(f"Sans token - Status: {response.status_code}")
    assert response.status_code == 403, "Should be unauthorized"
    print("✓ Accès correctement refusé sans token")
    
    # Essayer avec un mauvais token
    bad_headers = {"Authorization": "Bearer fake_token_12345"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=bad_headers)
    print(f"Mauvais token - Status: {response.status_code}")
    assert response.status_code == 401, "Should be unauthorized"
    print("✓ Accès correctement refusé avec mauvais token")

def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "█"*60)
    print("  TEST DE L'API GESTION MATÉRIELS")
    print("█"*60)
    
    tests = [
        ("Health Check", test_health),
        ("Inscription", test_register),
        ("Connexion", test_login),
        ("Infos Utilisateur", test_me),
        ("Dates d'Importation", test_get_dates),
        ("Statistiques", test_statistics),
        ("Dashboard", test_dashboard),
        ("Liste Matériels", test_materiels_list),
        ("Recherche par Code", test_search_by_code),
        ("Historique Uploads", test_upload_history),
        ("Changement Mot de Passe", test_change_password),
        ("Accès Non Autorisé", test_unauthorized_access)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, "✓ PASS"))
        except Exception as e:
            results.append((name, f"✗ FAIL: {str(e)}"))
            print(f"❌ Erreur: {str(e)}")
    
    # Résumé
    print("\n" + "█"*60)
    print("  RÉSUMÉ DES TESTS")
    print("█"*60)
    
    for name, result in results:
        print(f"{result:15} - {name}")
    
    passed = sum(1 for _, r in results if "PASS" in r)
    total = len(results)
    
    print("\n" + "="*60)
    print(f"  TOTAL: {passed}/{total} tests réussis ({passed*100//total}%)")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n\nErreur fatale: {str(e)}")