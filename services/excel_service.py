import pandas as pd
from config.database import execute_query, execute_many, Database
from datetime import date
from typing import Optional
import mysql.connector

class ExcelService:
    @staticmethod
    def process_excel_file(file_path: str, user_id: int, filename: str):
        """Traite un fichier Excel et insère les données dans la BD"""
        
        # Lire le fichier Excel
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Colonnes attendues
        colonnes_attendues = {
            'code': 'code',
            'region': 'region',
            'district': 'district',
            'commune': 'commune',
            'nom_materiel': 'nom_materiel',
            'etat_materiel': 'etat_materiel',
            'type_materiel': 'type_materiel',
            'motif': 'motif',
            'achat_consommable': 'achat_consommable',
            'compatibilite_consomm': 'compatibilite_consomm'
        }
        
        # Renommer les colonnes pour uniformiser
        df.columns = df.columns.str.strip()
        
        # Remplacer NaN par None (NULL en SQL)
        df = df.where(pd.notna(df), None)
        
        # Hériter des valeurs pour code, region, district, commune
        colonnes_heritage = ['code', 'region', 'district', 'commune']
        for col in colonnes_heritage:
            if col in df.columns:
                df[col] = df[col].fillna(method='ffill')
        
        # Créer une date d'importation
        query_date = "INSERT INTO date_import (date_complet) VALUES (CURRENT_DATE)"
        id_date_import = execute_query(query_date)
        
        # Enregistrer l'upload dans l'historique
        query_history = """
            INSERT INTO upload_history (filename, user_id) 
            VALUES (%s, %s)
        """
        execute_query(query_history, (filename, user_id))
        
        lignes_inserees = 0
        
        # Traiter chaque ligne
        with Database.get_cursor() as cursor:
            for _, row in df.iterrows():
                try:
                    # Extraire les données
                    code = row.get('code')
                    region = row.get('region')
                    district = row.get('district')
                    commune = row.get('commune')
                    nom_materiel = row.get('nom_materiel')
                    etat = row.get('etat_materiel')
                    type_materiel = row.get('type_materiel')
                    motif = row.get('motif')
                    achat_consommable = row.get('achat_consommable')
                    compatibilite_consomm = row.get('compatibilite_consomm')
                    
                    # Normaliser les valeurs vides
                    code = None if pd.isna(code) or str(code).strip() == '' else str(code).strip()
                    region = None if pd.isna(region) or str(region).strip() == '' else str(region).strip()
                    district = None if pd.isna(district) or str(district).strip() == '' else str(district).strip()
                    commune = None if pd.isna(commune) or str(commune).strip() == '' else str(commune).strip()
                    nom_materiel = None if pd.isna(nom_materiel) or str(nom_materiel).strip() == '' else str(nom_materiel).strip()
                    etat = None if pd.isna(etat) or str(etat).strip() == '' else str(etat).strip()
                    type_materiel = None if pd.isna(type_materiel) or str(type_materiel).strip() == '' else str(type_materiel).strip()
                    
                    # Skip si nom_materiel est vide
                    if not nom_materiel:
                        continue
                    
                    # 1. Gérer la localisation
                    code_localisation_id = ExcelService._get_or_create_localisation(
                        cursor, code, region, district, commune
                    )
                    
                    # 2. Gérer le matériel physique (référentiel persistant)
                    id_physique = ExcelService._get_or_create_materiel_physique(
                        cursor, code_localisation_id, nom_materiel, type_materiel
                    )
                    
                    # 3. Créer un snapshot dans materiel_informatique
                    query_snapshot = """
                        INSERT INTO materiel_informatique 
                        (id_physique, etat, id_date_import) 
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(query_snapshot, (id_physique, etat, id_date_import))
                    id_snapshot = cursor.lastrowid
                    
                    # 4. Gérer les incidents (si motif existe)
                    if motif and str(motif).strip() != '':
                        query_incident = """
                            INSERT INTO incident 
                            (motif, compatibilite_consommable, achat_consommable, id_materiel) 
                            VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(query_incident, (
                            motif, 
                            compatibilite_consomm, 
                            achat_consommable, 
                            id_snapshot
                        ))
                    
                    lignes_inserees += 1
                    
                except Exception as e:
                    print(f"Erreur lors du traitement de la ligne: {e}")
                    continue
        
        return {
            "lignes_inserees": lignes_inserees,
            "id_date_import": id_date_import,
            "date_import": date.today()
        }
    
    @staticmethod
    def _get_or_create_localisation(cursor, code, region, district, commune):
        """Récupère ou crée une localisation"""
        # Vérifier si la localisation existe
        query_check = """
            SELECT code_localisation 
            FROM localisation 
            WHERE code = %s AND region = %s AND district = %s AND commune = %s
        """
        cursor.execute(query_check, (code, region, district, commune))
        result = cursor.fetchone()
        
        if result:
            return result['code_localisation']
        
        # Créer la localisation
        query_insert = """
            INSERT INTO localisation (code, region, district, commune) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query_insert, (code, region, district, commune))
        return cursor.lastrowid
    
    @staticmethod
    def _get_or_create_materiel_physique(cursor, code_localisation_id, nom_materiel, type_materiel):
        """Récupère ou crée un matériel physique"""
        # Vérifier si le matériel physique existe déjà
        query_check = """
            SELECT id_physique 
            FROM materiel_physique 
            WHERE code_localisation_ref = %s 
            AND nom_materiel = %s 
            AND type = %s
        """
        cursor.execute(query_check, (code_localisation_id, nom_materiel, type_materiel))
        result = cursor.fetchone()
        
        if result:
            return result['id_physique']
        
        # Créer le matériel physique
        query_insert = """
            INSERT INTO materiel_physique 
            (code_localisation_ref, nom_materiel, type) 
            VALUES (%s, %s, %s)
        """
        cursor.execute(query_insert, (code_localisation_id, nom_materiel, type_materiel))
        return cursor.lastrowid
    
    @staticmethod
    def get_upload_history(skip: int = 0, limit: int = 10):
        """Récupère l'historique des uploads"""
        query_count = "SELECT COUNT(*) as total FROM upload_history"
        total_result = execute_query(query_count, fetch=True)
        total = total_result[0]['total'] if total_result else 0
        
        query = """
            SELECT 
                uh.id_upload,
                uh.filename,
                uh.upload_date,
                u.mail as user_mail
            FROM upload_history uh
            LEFT JOIN users u ON uh.user_id = u.id
            ORDER BY uh.upload_date DESC
            LIMIT %s OFFSET %s
        """
        results = execute_query(query, (limit, skip), fetch=True)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": results
        }