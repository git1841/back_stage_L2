from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, upload, statistics, materiels

# Créer l'application FastAPI
app = FastAPI(
    title="API Gestion Matériels Informatiques",
    description="API pour la gestion et le suivi des équipements informatiques avec import Excel",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(statistics.router)
app.include_router(materiels.router)

@app.get("/", tags=["Root"])
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "API Gestion Matériels Informatiques",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "auth": "/auth",
            "upload": "/upload",
            "statistics": "/statistics",
            "materiels": "/materiels"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Vérifier l'état de l'API"""
    from config.database import Database
    try:
        connection = Database.get_connection()
        connection.close()
        db_status = "OK"
    except Exception as e:
        db_status = f"ERROR: {str(e)}"
    
    return {
        "status": "running",
        "database": db_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )