from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Query
from routes.auth import get_current_user
from services.excel_service import ExcelService
from models.schemas import UploadResponse, UploadHistoryItem
import os
import uuid
from typing import List

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/excel", response_model=UploadResponse)
async def upload_excel(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload un fichier Excel et l'importer dans la base de données"""
    
    # Vérifier l'extension du fichier
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seuls les fichiers Excel (.xlsx, .xls) sont acceptés"
        )
    
    # Créer un nom de fichier unique
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = f"./uploads/{unique_filename}"
    
    # Créer le dossier uploads s'il n'existe pas
    os.makedirs("./uploads", exist_ok=True)
    
    try:
        # Sauvegarder le fichier temporairement
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Traiter le fichier Excel
        result = ExcelService.process_excel_file(
            file_path, 
            current_user['user_id'],
            file.filename
        )
        
        # Supprimer le fichier temporaire
        os.remove(file_path)
        
        return {
            "message": "Fichier importé avec succès",
            "filename": file.filename,
            "lignes_inserees": result['lignes_inserees'],
            "date_import": result['date_import'],
            "id_date_import": result['id_date_import']
        }
        
    except Exception as e:
        # Nettoyer le fichier temporaire en cas d'erreur
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement du fichier: {str(e)}"
        )

@router.get("/history")
async def get_upload_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Récupérer l'historique des uploads"""
    result = ExcelService.get_upload_history(skip, limit)
    return result

@router.get("/dates")
async def get_import_dates(current_user: dict = Depends(get_current_user)):
    """Récupérer toutes les dates d'importation disponibles"""
    from config.database import execute_query
    
    query = """
        SELECT id_date, date_complet
        FROM date_import
        ORDER BY date_complet DESC
    """
    results = execute_query(query, fetch=True)
    
    return {
        "total": len(results),
        "dates": results
    }