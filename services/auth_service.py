from config.database import execute_query
from utils.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException, status
from datetime import timedelta

class AuthService:
    @staticmethod
    def register_user(mail: str, mot_de_passe: str):
        """Enregistre un nouvel utilisateur"""
        # Vérifier si l'utilisateur existe déjà
        query_check = "SELECT id FROM users WHERE mail = %s"
        existing = execute_query(query_check, (mail,), fetchone=True)
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé"
            )
        
        # Hasher le mot de passe
        hashed_password = hash_password(mot_de_passe)
        
        # Insérer l'utilisateur
        query_insert = "INSERT INTO users (mail, mot_de_passe) VALUES (%s, %s)"
        user_id = execute_query(query_insert, (mail, hashed_password))
        
        # Récupérer l'utilisateur créé
        query_get = "SELECT id, mail, created_at FROM users WHERE id = %s"
        user = execute_query(query_get, (user_id,), fetchone=True)
        
        return user
    
    @staticmethod
    def login_user(mail: str, mot_de_passe: str):
        """Authentifie un utilisateur et retourne un token"""
        # Récupérer l'utilisateur
        query = "SELECT id, mail, mot_de_passe FROM users WHERE mail = %s"
        user = execute_query(query, (mail,), fetchone=True)
        
        if not user or not verify_password(mot_de_passe, user['mot_de_passe']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Créer le token
        access_token = create_access_token(
            data={"sub": user['mail'], "user_id": user['id']},
            expires_delta=timedelta(minutes=1440)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user['id'],
                "mail": user['mail']
            }
        }
    
    @staticmethod
    def change_password(user_id: int, ancien_mot_de_passe: str, nouveau_mot_de_passe: str):
        """Change le mot de passe d'un utilisateur"""
        # Récupérer l'utilisateur
        query = "SELECT mot_de_passe FROM users WHERE id = %s"
        user = execute_query(query, (user_id,), fetchone=True)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        # Vérifier l'ancien mot de passe
        if not verify_password(ancien_mot_de_passe, user['mot_de_passe']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ancien mot de passe incorrect"
            )
        
        # Hasher et mettre à jour le nouveau mot de passe
        hashed_password = hash_password(nouveau_mot_de_passe)
        query_update = "UPDATE users SET mot_de_passe = %s WHERE id = %s"
        execute_query(query_update, (hashed_password, user_id))
        
        return {"message": "Mot de passe modifié avec succès"}
    
    @staticmethod
    def change_mail(user_id: int, nouveau_mail: str, mot_de_passe: str):
        """Change l'email d'un utilisateur"""
        # Récupérer l'utilisateur
        query = "SELECT mot_de_passe FROM users WHERE id = %s"
        user = execute_query(query, (user_id,), fetchone=True)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        # Vérifier le mot de passe
        if not verify_password(mot_de_passe, user['mot_de_passe']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mot de passe incorrect"
            )
        
        # Vérifier si le nouvel email est déjà utilisé
        query_check = "SELECT id FROM users WHERE mail = %s AND id != %s"
        existing = execute_query(query_check, (nouveau_mail, user_id), fetchone=True)
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé"
            )
        
        # Mettre à jour l'email
        query_update = "UPDATE users SET mail = %s WHERE id = %s"
        execute_query(query_update, (nouveau_mail, user_id))
        
        return {"message": "Email modifié avec succès", "nouveau_mail": nouveau_mail}