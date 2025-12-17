from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import date, datetime

# Schémas d'authentification
class UserCreate(BaseModel):
    mail: EmailStr
    mot_de_passe: str = Field(min_length=6)

class UserLogin(BaseModel):
    mail: EmailStr
    mot_de_passe: str

class UserResponse(BaseModel):
    id: int
    mail: str
    created_at: datetime

class ChangePassword(BaseModel):
    ancien_mot_de_passe: str
    nouveau_mot_de_passe: str = Field(min_length=6)

class ChangeMail(BaseModel):
    nouveau_mail: EmailStr
    mot_de_passe: str

# Schémas pour les matériels
class MaterielBase(BaseModel):
    code: Optional[str]
    region: Optional[str]
    district: Optional[str]
    commune: Optional[str]
    nom_materiel: Optional[str]
    etat: Optional[str]
    type: Optional[str]

class MaterielResponse(MaterielBase):
    id_snapshot: int
    id_physique: int
    date_import: date
    
class MaterielDetail(MaterielResponse):
    motif: Optional[str]
    achat_consommable: Optional[str]
    compatibilite_consommable: Optional[str]

# Schémas pour statistiques
class DistrictPanneStats(BaseModel):
    code: str
    district: str
    nombre_pannes: int
    taux_pannes: float
    total_materielle: int

class TypeMaterielPanne(BaseModel):
    type: str
    nombre_pannes: int

class RegionStats(BaseModel):
    code: str
    region: str
    total_materiels: int
    taux_fonctionnel: float

class ImportationEtat(BaseModel):
    date_importation: date
    fonctionnels: int
    non_fonctionnels: int

class ResumeGlobal(BaseModel):
    total_materiels: int
    materiels_fonctionnels: int
    materiels_en_panne: int
    taux_fonctionnement: float
    taux_en_panne: float

class StatistiquesResponse(BaseModel):
    nouveau_materiel: int
    materiel_perdu: int
    top_5_districts_pannes: List[DistrictPanneStats]
    pannes_par_type_materiel: List[TypeMaterielPanne]
    materiels_par_region: List[RegionStats]
    etat_6_dernieres_importations: List[ImportationEtat]
    resume_global: ResumeGlobal

# Schémas pour upload
class UploadResponse(BaseModel):
    message: str
    filename: str
    lignes_inserees: int
    date_import: date
    id_date_import: int

class UploadHistoryItem(BaseModel):
    id_upload: int
    filename: str
    upload_date: datetime
    user_mail: str

# Schémas pour pagination
class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)

class PaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List