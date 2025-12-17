from config.database import execute_query
from typing import Optional

class StatisticsService:
    
    @staticmethod
    def get_statistics(id_date_import: int, skip_type: int = 0, limit_type: int = 100, 
                       skip_region: int = 0, limit_region: int = 100):
        """Calcule toutes les statistiques pour une date d'importation donnée"""
        
        # 1. Nouveau matériel et matériel perdu
        nouveau_materiel, materiel_perdu = StatisticsService._calculate_materiel_changes(id_date_import)
        
        # 2. Top 5 districts avec le plus de pannes
        top_5_districts = StatisticsService._get_top_5_districts_pannes(id_date_import)
        
        # 3. Pannes par type de matériel
        pannes_par_type = StatisticsService._get_pannes_par_type(id_date_import, skip_type, limit_type)
        
        # 4. Matériels par région
        materiels_par_region = StatisticsService._get_materiels_par_region(id_date_import, skip_region, limit_region)
        
        # 5. État des 6 dernières importations
        etat_6_dernieres = StatisticsService._get_etat_6_dernieres_importations(id_date_import)
        
        # 6. Résumé global
        resume_global = StatisticsService._get_resume_global(id_date_import)
        
        return {
            "nouveau_materiel": nouveau_materiel,
            "materiel_perdu": materiel_perdu,
            "top_5_districts_pannes": top_5_districts,
            "pannes_par_type_materiel": pannes_par_type,
            "materiels_par_region": materiels_par_region,
            "etat_6_dernieres_importations": etat_6_dernieres,
            "resume_global": resume_global
        }
    
    @staticmethod
    def _calculate_materiel_changes(id_date_import: int):
        """Calcule les nouveaux matériels et matériels perdus"""
        
        # Trouver la date précédente
        query_prev = """
            SELECT id_date 
            FROM date_import 
            WHERE id_date < %s 
            ORDER BY id_date DESC 
            LIMIT 1
        """
        prev_date = execute_query(query_prev, (id_date_import,), fetchone=True)
        
        if not prev_date:
            # Première importation
            query_count = """
                SELECT COUNT(DISTINCT id_physique) as total
                FROM materiel_informatique
                WHERE id_date_import = %s
            """
            result = execute_query(query_count, (id_date_import,), fetchone=True)
            return result['total'], 0
        
        prev_id = prev_date['id_date']
        
        # Compter les matériels de la date actuelle
        query_current = """
            SELECT COUNT(DISTINCT id_physique) as total
            FROM materiel_informatique
            WHERE id_date_import = %s
        """
        current_count = execute_query(query_current, (id_date_import,), fetchone=True)
        total_current = current_count['total'] if current_count else 0
        
        # Compter les matériels de la date précédente
        query_previous = """
            SELECT COUNT(DISTINCT id_physique) as total
            FROM materiel_informatique
            WHERE id_date_import = %s
        """
        previous_count = execute_query(query_previous, (prev_id,), fetchone=True)
        total_previous = previous_count['total'] if previous_count else 0
        
        # Calculer la différence
        difference = total_current - total_previous
        
        nouveau_materiel = max(0, difference)
        materiel_perdu = max(0, -difference)
        
        return nouveau_materiel, materiel_perdu
    
    @staticmethod
    def _get_top_5_districts_pannes(id_date_import: int):
        """Récupère le top 5 des districts avec le plus de pannes"""
        
        query = """
            SELECT 
                l.code,
                l.district,
                COUNT(CASE WHEN mi.etat = 'Non fonctionnel' THEN 1 END) as nombre_pannes,
                COUNT(mi.id_snapshot) as total_materielle,
                ROUND(
                    (COUNT(CASE WHEN mi.etat = 'Non fonctionnel' THEN 1 END) * 100.0) / 
                    NULLIF(COUNT(mi.id_snapshot), 0), 
                    2
                ) as taux_pannes
            FROM materiel_informatique mi
            JOIN materiel_physique mp ON mi.id_physique = mp.id_physique
            JOIN localisation l ON mp.code_localisation_ref = l.code_localisation
            WHERE mi.id_date_import = %s
            GROUP BY l.code, l.district
            HAVING nombre_pannes > 0
            ORDER BY nombre_pannes DESC
            LIMIT 5
        """
        
        results = execute_query(query, (id_date_import,), fetch=True)
        
        return [
            {
                "code": r['code'],
                "district": r['district'],
                "nombre_pannes": r['nombre_pannes'],
                "taux_pannes": float(r['taux_pannes']) if r['taux_pannes'] else 0,
                "total_materielle": r['total_materielle']
            }
            for r in results
        ]
    
    @staticmethod
    def _get_pannes_par_type(id_date_import: int, skip: int = 0, limit: int = 100):
        """Récupère les pannes par type de matériel avec pagination"""
        
        query = """
            SELECT 
                mp.type,
                COUNT(mi.id_snapshot) as nombre_pannes
            FROM materiel_informatique mi
            JOIN materiel_physique mp ON mi.id_physique = mp.id_physique
            WHERE mi.id_date_import = %s 
            AND mi.etat = 'Non fonctionnel'
            GROUP BY mp.type
            ORDER BY nombre_pannes DESC
            LIMIT %s OFFSET %s
        """
        
        results = execute_query(query, (id_date_import, limit, skip), fetch=True)
        
        return [
            {
                "type": r['type'],
                "nombre_pannes": r['nombre_pannes']
            }
            for r in results
        ]
    
    @staticmethod
    def _get_materiels_par_region(id_date_import: int, skip: int = 0, limit: int = 100):
        """Récupère les statistiques par région avec pagination"""
        
        query = """
            SELECT 
                l.code,
                l.region,
                COUNT(mi.id_snapshot) as total_materiels,
                ROUND(
                    (COUNT(CASE WHEN mi.etat = 'Fonctionnel' THEN 1 END) * 100.0) / 
                    NULLIF(COUNT(mi.id_snapshot), 0), 
                    2
                ) as taux_fonctionnel
            FROM materiel_informatique mi
            JOIN materiel_physique mp ON mi.id_physique = mp.id_physique
            JOIN localisation l ON mp.code_localisation_ref = l.code_localisation
            WHERE mi.id_date_import = %s
            GROUP BY l.code, l.region
            ORDER BY total_materiels DESC
            LIMIT %s OFFSET %s
        """
        
        results = execute_query(query, (id_date_import, limit, skip), fetch=True)
        
        return [
            {
                "code": r['code'],
                "region": r['region'],
                "total_materiels": r['total_materiels'],
                "taux_fonctionnel": float(r['taux_fonctionnel']) if r['taux_fonctionnel'] else 0
            }
            for r in results
        ]
    
    @staticmethod
    def _get_etat_6_dernieres_importations(id_date_import: int):
        """Récupère l'état des 6 dernières importations"""
        
        query = """
            SELECT 
                di.date_complet as date_importation,
                COUNT(CASE WHEN mi.etat = 'Fonctionnel' THEN 1 END) as fonctionnels,
                COUNT(CASE WHEN mi.etat = 'Non fonctionnel' THEN 1 END) as non_fonctionnels
            FROM date_import di
            LEFT JOIN materiel_informatique mi ON di.id_date = mi.id_date_import
            WHERE di.id_date <= %s
            GROUP BY di.id_date, di.date_complet
            ORDER BY di.id_date DESC
            LIMIT 6
        """
        
        results = execute_query(query, (id_date_import,), fetch=True)
        
        # Inverser pour avoir l'ordre chronologique
        results.reverse()
        
        return [
            {
                "date_importation": r['date_importation'],
                "fonctionnels": r['fonctionnels'],
                "non_fonctionnels": r['non_fonctionnels']
            }
            for r in results
        ]
    
    @staticmethod
    def _get_resume_global(id_date_import: int):
        """Calcule le résumé global"""
        
        query = """
            SELECT 
                COUNT(mi.id_snapshot) as total_materiels,
                COUNT(CASE WHEN mi.etat = 'Fonctionnel' THEN 1 END) as materiels_fonctionnels,
                COUNT(CASE WHEN mi.etat = 'Non fonctionnel' THEN 1 END) as materiels_en_panne
            FROM materiel_informatique mi
            WHERE mi.id_date_import = %s
        """
        
        result = execute_query(query, (id_date_import,), fetchone=True)
        
        total = result['total_materiels'] if result else 0
        fonctionnels = result['materiels_fonctionnels'] if result else 0
        en_panne = result['materiels_en_panne'] if result else 0
        
        taux_fonctionnement = round((fonctionnels * 100.0 / total), 2) if total > 0 else 0
        taux_en_panne = round((en_panne * 100.0 / total), 2) if total > 0 else 0
        
        return {
            "total_materiels": total,
            "materiels_fonctionnels": fonctionnels,
            "materiels_en_panne": en_panne,
            "taux_fonctionnement": taux_fonctionnement,
            "taux_en_panne": taux_en_panne
        }