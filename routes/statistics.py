from fastapi import APIRouter, Depends, Query, HTTPException, status
from routes.auth import get_current_user
from services.statistics_service import StatisticsService
from models.schemas import StatistiquesResponse

router = APIRouter(prefix="/statistics", tags=["Statistiques"])

@router.get("/", response_model=StatistiquesResponse)
async def get_statistics(
    id_date_import: int = Query(..., description="ID de la date d'importation"),
    skip_type: int = Query(0, ge=0, description="Skip pour pannes par type"),
    limit_type: int = Query(100, ge=1, le=100, description="Limit pour pannes par type"),
    skip_region: int = Query(0, ge=0, description="Skip pour matériels par région"),
    limit_region: int = Query(100, ge=1, le=100, description="Limit pour matériels par région"),
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer toutes les statistiques pour une date d'importation donnée.
    
    Cette route calcule:
    - Les nouveaux matériels et matériels perdus
    - Le top 5 des districts avec le plus de pannes
    - Les pannes par type de matériel (avec pagination)
    - Les matériels par région (avec pagination)
    - L'état des 6 dernières importations
    - Le résumé global
    """
    
    # Vérifier que la date d'importation existe
    from config.database import execute_query
    query_check = "SELECT id_date FROM date_import WHERE id_date = %s"
    date_exists = execute_query(query_check, (id_date_import,), fetchone=True)
    
    if not date_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Date d'importation non trouvée"
        )
    
    result = StatisticsService.get_statistics(
        id_date_import,
        skip_type,
        limit_type,
        skip_region,
        limit_region
    )
    
    return result

@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer les statistiques du tableau de bord (dernière importation)
    """
    from config.database import execute_query
    
    # Récupérer la dernière date d'importation
    query = "SELECT id_date FROM date_import ORDER BY id_date DESC LIMIT 1"
    last_import = execute_query(query, fetchone=True)
    
    if not last_import:
        return {
            "message": "Aucune importation trouvée",
            "statistics": None
        }
    
    result = StatisticsService.get_statistics(
        last_import['id_date'],
        skip_type=0,
        limit_type=20,
        skip_region=0,
        limit_region=20
    )
    
    return {
        "id_date_import": last_import['id_date'],
        "statistics": result
    }