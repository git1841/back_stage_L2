"""
Gestionnaires d'erreurs personnalisés pour l'API
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from mysql.connector import Error as MySQLError
import traceback

class DatabaseError(Exception):
    """Exception personnalisée pour les erreurs de base de données"""
    def __init__(self, message: str, original_error=None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

class FileProcessingError(Exception):
    """Exception personnalisée pour les erreurs de traitement de fichiers"""
    def __init__(self, message: str, filename: str = None):
        self.message = message
        self.filename = filename
        super().__init__(self.message)

class AuthenticationError(Exception):
    """Exception personnalisée pour les erreurs d'authentification"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

async def database_exception_handler(request: Request, exc: DatabaseError):
    """Gestionnaire pour les erreurs de base de données"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "message": exc.message,
            "detail": "Une erreur s'est produite lors de l'accès à la base de données"
        }
    )

async def file_processing_exception_handler(request: Request, exc: FileProcessingError):
    """Gestionnaire pour les erreurs de traitement de fichiers"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "File Processing Error",
            "message": exc.message,
            "filename": exc.filename
        }
    )

async def mysql_exception_handler(request: Request, exc: MySQLError):
    """Gestionnaire pour les erreurs MySQL"""
    print(f"MySQL Error: {exc}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "message": "Une erreur s'est produite lors de l'accès à la base de données",
            "detail": str(exc) if hasattr(exc, '__str__') else "Unknown MySQL error"
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Gestionnaire pour les erreurs de validation Pydantic"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Les données fournies ne sont pas valides",
            "details": exc.errors()
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Gestionnaire générique pour toutes les autres exceptions"""
    print(f"Unhandled Exception: {exc}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "Une erreur inattendue s'est produite",
            "detail": str(exc)
        }
    )

def register_error_handlers(app):
    """Enregistre tous les gestionnaires d'erreurs dans l'application FastAPI"""
    app.add_exception_handler(DatabaseError, database_exception_handler)
    app.add_exception_handler(FileProcessingError, file_processing_exception_handler)
    app.add_exception_handler(MySQLError, mysql_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)