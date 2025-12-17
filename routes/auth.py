from fastapi import APIRouter, Depends, HTTPException, status
#from fastapi.security import HTTPBearer, HTTPAuthCredentials
from models.schemas import UserCreate, UserLogin, UserResponse, ChangePassword, ChangeMail
from services.auth_service import AuthService
from utils.security import verify_token

from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials


router = APIRouter(prefix="/auth", tags=["Authentification"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dépendance pour récupérer l'utilisateur courant"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return payload

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Enregistrer un nouvel utilisateur"""
    result = AuthService.register_user(user.mail, user.mot_de_passe)
    return result

@router.post("/login")
async def login(credentials: UserLogin):
    """Se connecter et obtenir un token"""
    result = AuthService.login_user(credentials.mail, credentials.mot_de_passe)
    return result

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: dict = Depends(get_current_user)
):
    """Changer le mot de passe"""
    result = AuthService.change_password(
        current_user['user_id'],
        password_data.ancien_mot_de_passe,
        password_data.nouveau_mot_de_passe
    )
    return result

@router.post("/change-mail")
async def change_mail(
    mail_data: ChangeMail,
    current_user: dict = Depends(get_current_user)
):
    """Changer l'email"""
    result = AuthService.change_mail(
        current_user['user_id'],
        mail_data.nouveau_mail,
        mail_data.mot_de_passe
    )
    return result

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Récupérer les informations de l'utilisateur courant"""
    from config.database import execute_query
    
    query = "SELECT id, mail, created_at FROM users WHERE id = %s"
    user = execute_query(query, (current_user['user_id'],), fetchone=True)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return user