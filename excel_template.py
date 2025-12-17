"""
Script pour créer un fichier Excel d'exemple
Ce fichier peut être utilisé comme template pour les imports
"""

import pandas as pd
from datetime import datetime

def create_example_excel():
    """Crée un fichier Excel d'exemple avec des données de test"""
    
    # Données d'exemple
    data = {
        'code': ['630601', '', '610201', '', '620201', '', '630301', '', '610101'],
        'region': ['ATSIMO ANDREFANA', '', 'ANDROY', '', 'ANOSY', '', 'ATSIMO ANDREFANA', '', 'A'],
        'district': ['MOROMBE', '', 'BEKILY', '', 'BETROKA', '', 'BENENITRA', '', 'AMBOYOMBE'],
        'commune': ['A', '', 'Ambahita', '', 'Ambalaso', '', 'Ambalavato', '', 'Ambanisarike'],
        'nom_materiel': [
            'Imprimante 1', 'Imprimante 2',
            'Imprimante 1', 'Imprimante 2',
            'Imprimante 1', 'Imprimante 2',
            'Imprimante 1', 'ASUS 2',
            'Itel 1'
        ],
        'etat_materiel': [
            'Fonctionnel', 'Fonctionnel',
            'Non fonctionnel', 'Non fonctionnel',
            'Fonctionnel', 'Fonctionnel',
            '', '',
            'Fonctionnel'
        ],
        'type_materiel': [
            'Imprimante', 'Imprimante',
            'Imprimante', 'Imprimante',
            'Imprimante', 'Imprimante',
            'Imprimante', 'Ordinateur',
            'Telephone'
        ],
        'motif': [
            'ER P03', '',
            'ba. Problème cartouche', 'ba!! Problème cartouche',
            'Tsy misy olana', 'Tsy misy olana',
            '', '',
            ''
        ],
        'achat_consommable': [
            'ENY', 'ENY',
            'ENY', 'ENY',
            'TSIA', 'TSIA',
            '', '',
            'ENY'
        ],
        'compatibilite_consomm': [
            'NETY', 'NETY',
            'Mety taminy', 'Tena mety aminy',
            '', '',
            '', '',
            'tsy mitovy teo @ taloha ny Encre'
        ]
    }
    
    # Créer le DataFrame
    df = pd.DataFrame(data)
    
    # Remplacer les chaînes vides par des valeurs None (qui deviendront NaN dans Excel)
    df = df.replace('', None)
    
    # Nom du fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exemple_materiels_{timestamp}.xlsx"
    
    # Créer le fichier Excel
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Matériels')
        
        # Obtenir la worksheet pour ajuster les largeurs de colonnes
        worksheet = writer.sheets['Matériels']
        
        # Ajuster automatiquement la largeur des colonnes
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            ) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = max_length
    
    print(f"✓ Fichier créé: {filename}")
    print(f"  - {len(df)} lignes")
    print(f"  - {len(df.columns)} colonnes")
    print("\nCe fichier peut être utilisé pour tester l'upload dans l'API")
    print("Endpoint: POST /upload/excel")
    
    return filename

def create_large_example():
    """Crée un fichier Excel plus grand pour tester les performances"""
    
    import random
    
    regions = ['ATSIMO ANDREFANA', 'ANDROY', 'ANOSY', 'VAKINANKARATRA']
    districts = ['MOROMBE', 'BEKILY', 'BETROKA', 'ANTSIRABE']
    communes = ['Commune A', 'Commune B', 'Commune C', 'Commune D']
    types = ['Imprimante', 'Ordinateur', 'Routeur', 'Scanner', 'Onduleur']
    etats = ['Fonctionnel', 'Non fonctionnel', None]
    
    data = []
    
    for i in range(100):
        code = f"{random.randint(600000, 699999)}"
        region = random.choice(regions)
        district = random.choice(districts)
        commune = random.choice(communes)
        
        # 2-3 matériels par localisation
        nb_materiels = random.randint(2, 3)
        
        for j in range(nb_materiels):
            if j == 0:
                # Premier matériel a toutes les infos
                row_code = code
                row_region = region
                row_district = district
                row_commune = commune
            else:
                # Matériels suivants ont des cellules vides
                row_code = ''
                row_region = ''
                row_district = ''
                row_commune = ''
            
            type_mat = random.choice(types)
            etat = random.choice(etats)
            
            data.append({
                'code': row_code,
                'region': row_region,
                'district': row_district,
                'commune': row_commune,
                'nom_materiel': f"{type_mat} {j+1}",
                'etat_materiel': etat,
                'type_materiel': type_mat,
                'motif': 'Problème technique' if etat == 'Non fonctionnel' else '',
                'achat_consommable': random.choice(['ENY', 'TSIA', '']),
                'compatibilite_consomm': random.choice(['NETY', 'Mety', ''])
            })
    
    df = pd.DataFrame(data)
    df = df.replace('', None)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_performance_{timestamp}.xlsx"
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Matériels')
        
        worksheet = writer.sheets['Matériels']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            ) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = max_length
    
    print(f"✓ Fichier de test performance créé: {filename}")
    print(f"  - {len(df)} lignes")
    print(f"  - Environ {len(df)//3} localisations")
    
    return filename

if __name__ == "__main__":
    print("="*60)
    print("  CRÉATION DE FICHIERS EXCEL D'EXEMPLE")
    print("="*60)
    print()
    
    print("1. Création du fichier d'exemple simple...")
    create_example_excel()
    
    print("\n2. Création du fichier de test performance...")
    create_large_example()
    
    print("\n" + "="*60)
    print("  FICHIERS CRÉÉS AVEC SUCCÈS")
    print("="*60)
    print("\nVous pouvez maintenant uploader ces fichiers via l'API:")
    print("  curl -X POST http://localhost:8000/upload/excel \\")
    print("       -H 'Authorization: Bearer YOUR_TOKEN' \\")
    print("       -F 'file=@exemple_materiels_*.xlsx'")
    print()