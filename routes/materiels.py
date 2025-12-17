from fastapi import APIRouter, Depends, Query, HTTPException, status
from routes.auth import get_current_user
from config.database import execute_query
from typing import Optional

router = APIRouter(prefix="/materiels", tags=["Matériels"])

@router.get("/all")
async def get_all_materiels(
    id_date_import: int = Query(..., description="ID de la date d'importation"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer tous les matériels pour une date d'importation donnée"""
    
    # Compter le total
    query_count = """
        SELECT COUNT(*) as total
        FROM materiel_informatique mi
        WHERE mi.id_date_import = %s
    """
    count_result = execute_query(query_count, (id_date_import,), fetchone=True)
    total = count_result['total'] if count_result else 0
    
    # Récupérer les matériels avec pagination
    query = """
        SELECT 
            mi.id_snapshot,
            mi.id_physique,
            mi.etat,
            mp.nom_materiel,
            mp.type,
            l.code,
            l.region,
            l.district,
            l.commune,
            di.date_complet as date_import
        FROM materiel_informatique mi
        JOIN materiel_physique mp ON mi.id_physique = mp.id_physique
        JOIN localisation l ON mp.code_localisation_ref = l.code_localisation
        JOIN date_import di ON mi.id_date_import = di.id_date
        WHERE mi.id_date_import = %s
        ORDER BY mi.id_snapshot DESC
        LIMIT %s OFFSET %s
    """
    
    results = execute_query(query, (id_date_import, limit, skip), fetch=True)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": results
    }

@router.get("/by-commune")
async def get_materiels_by_commune(
    id_date_import: int = Query(..., description="ID de la date d'importation"),
    commune: str = Query(..., description="Nom de la commune"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer les matériels d'une commune pour une date d'importation donnée"""
    
    # Compter le total
    query_count = """
        SELECT COUNT(*) as total
        FROM materiel_informatique mi
        JOIN materiel_physique mp ON mi.id_physique = mp.id_physique
        JOIN localisation l ON mp.code_localisation_ref = l.code_localisation
        WHERE mi.id_date_import = %s AND l.commune = %s
    """
    count_result = execute_query(query_count, (id_date_import, commune), fetchone=True)
    total = count_result['total'] if count_result else 0
    
    # Récupérer les matériels
    query = """
        SELECT 
            mi.id_snapshot,
            mi.id_physique,
            mi.etat,
            mp.nom_materiel,
            mp.type,
            l.code,
            l.region,
            l.district,
            l.commune,
            di.date_complet as date_import
        FROM materiel_informatique mi
        JOIN materiel_physique mp ON mi.id_physique = mp.id_physique
        JOIN localisation l ON mp.code_localisation_ref = l.code_localisation
        JOIN date_import di ON mi.id_date_import = di.id_date
        WHERE mi.id_date_import = %s AND l.commune = %s
        ORDER BY mi.id_snapshot DESC
        LIMIT %s OFFSET %s
    """
    
    results = execute_query(query, (id_date_import, commune, limit, skip), fetch=True)
    
    return {
        "total": total,
        "commune": commune,
        "skip": skip,
        "limit": limit,
        "data": results
    }

@router.get("/nouveaux")
async def get_nouveaux_materiels(
    date_ancienne: int = Query(..., description="ID de la date d'importation ancienne"),
    date_nouvelle: int = Query(..., description="ID de la date d'importation nouvelle"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer les nouveaux matériels entre deux dates"""
    
    # Vérifier que date_nouvelle > date_ancienne
    if date_nouvelle <= date_ancienne:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La date nouvelle doit être postérieure à la date ancienne"
        )
    
    # Récupérer les matériels qui sont dans la nouvelle date mais pas dans l'ancienne
    query_count = """
        SELECT COUNT(DISTINCT mi_new.id_physique) as total
        FROM materiel_informatique mi_new
        WHERE mi_new.id_date_import = %s
        AND mi_new.id_physique NOT IN (
            SELECT DISTINCT id_physique
            FROM materiel_informatique
            WHERE id_date_import = %s
        )
    """
    count_result = execute_query(query_count, (date_nouvelle, date_ancienne), fetchone=True)
    total = count_result['total'] if count_result else 0
    
    query = """
        SELECT 
            mi.id_snapshot,
            mi.id_physique,
            mi.etat,
            mp.nom_materiel,
            mp.type,
            l.code,
            l.region,
            l.district,
            l.commune,
            di.date_complet as date_import
        FROM materiel_informatique mi
        JOIN materiel_physique mp ON mi.id_physique = mp.id_physique
        JOIN localisation l ON mp.code_localisation_ref = l.code_localisation
        JOIN date_import di ON mi.id_date_import = di.id_date
        WHERE mi.id_date_import = %s
        AND mi.id_physique NOT IN (
            SELECT DISTINCT id_physique
            FROM materiel_informatique
            WHERE id_date_import = %s
        )
        ORDER BY mi.id_snapshot DESC
        LIMIT %s OFFSET %s
    """
    
    results = execute_query(query, (date_nouvelle, date_ancienne, limit, skip), fetch=True)
    
    return {
        "total": total,
        "date_ancienne": date_ancienne,
        "date_nouvelle": date_nouvelle,
        "skip": skip,
        "limit": limit,
        "data": results
    }

@router.get("/{id_snapshot}")
async def get_materiel_detail(
    id_snapshot: int,
    current_user: dict = Depends(get_current_user)
):
    """Récupérer les détails d'un matériel spécifique"""
    
    query = """
        SELECT 
            mi.id_snapshot,
            mi.id_physique,
            mi.etat,
            mp.nom_materiel,
            mp.type,
            l.code,
            l.region,
            l.district,
            l.commune,
            di.date_complet as date_import,
            i.motif,
            i.achat_consommable,
            i.compatibilite_consommable
        FROM materiel_informatique mi
        JOIN materiel_physique mp ON mi.id_physique = mp.id_physique
        JOIN localisation l ON mp.code_localisation_ref = l.code_localisation
        JOIN date_import di ON mi.id_date_import = di.id_date
        LEFT JOIN incident i ON mi.id_snapshot = i.id_materiel
        WHERE mi.id_snapshot = %s
    """
    
    result = execute_query(query, (id_snapshot,), fetchone=True)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matériel non trouvé"
        )
    
    return result

@router.get("/search/by-code")
async def search_by_code(
    code: str = Query(..., description="Code de localisation"),
    id_date_import: Optional[int] = Query(None, description="ID de la date d'importation (optionnel)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Rechercher des matériels par code de localisation"""
    
    if id_date_import:
        # Recherche pour une date spécifique
        query_count = """
            SELECT COUNT(*) as total
            FROM materiel_informatique mi
            JOIN materiel_physique mp ON mi.id_physique = mp.id_physique
            JOIN localisation l ON mp.code_localisation_ref = l.code_localisation
            WHERE l.code = %s AND mi.id_date_import = %s
        """
        count_result = execute_query(query_count, (code, id_date_import), fetchone=True)
        
        query = """
            SELECT 
                mi.id_snapshot,
                mi.id_physique,
                mi.etat,
                mp.nom_materiel,
                mp.type,
                l.code,
                l.region,
                l.district,
                l.commune,
                di.date_complet as date_import
            FROM materiel_informatique mi
            JOIN materiel_physique mp ON mi.id_physique = mp.id_physique
            JOIN localisation l ON mp.code_localisation_ref = l.code_localisation
            JOIN date_import di ON mi.id_date_import = di.id_date
            WHERE l.code = %s AND mi.id_date_import = %s
            ORDER BY mi.id_snapshot DESC
            LIMIT %s OFFSET %s
        """
        results = execute_query(query, (code, id_date_import, limit, skip), fetch=True)
    else:
        # Recherche sur toutes les dates
        query_count = """
            SELECT COUNT(*) as total
            FROM materiel_informatique mi
            JOIN materiel_physique mp ON mi.id_physique = mp.id_physique
            JOIN localisation l ON mp.code_localisation_ref = l.code_localisation
            WHERE l.code = %s
        """
        count_result = execute_query(query_count, (code,), fetchone=True)
        
        query = """
            SELECT 
                mi.id_snapshot,
                mi.id_physique,
                mi.etat,
                mp.nom_materiel,
                mp.type,
                l.code,
                l.region,
                l.district,
                l.commune,
                di.date_complet as date_import
            FROM materiel_informatique mi
            JOIN materiel_physique mp ON mi.id_physique = mp.id_physique
            JOIN localisation l ON mp.code_localisation_ref = l.code_localisation
            JOIN date_import di ON mi.id_date_import = di.id_date
            WHERE l.code = %s
            ORDER BY mi.id_snapshot DESC
            LIMIT %s OFFSET %s
        """
        results = execute_query(query, (code, limit, skip), fetch=True)
    
    total = count_result['total'] if count_result else 0
    
    return {
        "total": total,
        "code": code,
        "skip": skip,
        "limit": limit,
        "data": results
    }