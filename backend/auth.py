import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from keycloak import KeycloakOpenID, KeycloakAdmin
from sqlalchemy.orm import Session
from database import get_db
from modelos.Usuarios.modelo import Usuario

# Configuración de Keycloak
# Usamos el nombre del servicio en Docker para la comunicación interna
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
REALM_NAME = os.getenv("KEYCLOAK_REALM", "Vinculo")
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "vinculo-app")
ADMIN_USER = os.getenv("KEYCLOAK_ADMIN", "admin")
ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")

keycloak_openid = KeycloakOpenID(
    server_url=f"{KEYCLOAK_URL}/",
    client_id=CLIENT_ID,
    realm_name=REALM_NAME,
)

def get_keycloak_admin():
    return KeycloakAdmin(
        server_url=f"{KEYCLOAK_URL}/",
        username=ADMIN_USER,
        password=ADMIN_PASSWORD,
        realm_name=REALM_NAME,
        user_realm_name="master", # Los admins suelen estar en el realm master
        verify=True
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Valida el token JWT contra Keycloak.
    """
    try:
        # Obtenemos la clave pública para validar la firma
        # En producción esto debería cachearse
        public_key = "-----BEGIN PUBLIC KEY-----\n" + \
                     keycloak_openid.public_key() + \
                     "\n-----END PUBLIC KEY-----"
        
        # Opciones de validación
        options = {
            "verify_signature": True,
            "verify_aud": False,  # Keycloak a veces pone el client_id en 'azp' o 'aud' múltiple
            "verify_exp": True
        }

        payload = jwt.decode(
            token, 
            public_key, 
            algorithms=["RS256"], 
            options=options
        )

        # SINCRONIZACIÓN: Asegurar que el usuario existe en nuestra DB local
        usuario_id = payload.get("sub")
        if usuario_id:
            import uuid
            try:
                user_uuid = uuid.UUID(usuario_id)
            except ValueError:
                user_uuid = None
                
            if user_uuid:
                db_user = db.query(Usuario).filter(Usuario.id == user_uuid).first()
                if not db_user:
                    email = payload.get("email", f"{usuario_id}@keycloak.local")
                    
                    # Verificar si existe por email (auto-sanación si se borró de Keycloak pero no de local)
                    existing_email = db.query(Usuario).filter(Usuario.email == email).first()
                    if existing_email:
                        # Si existe el email con otro ID, actualizamos el registro de Keycloak
                        # Esto asume que el email es la fuente de verdad.
                        # Dado que ID es primary key, no podemos cambiarlo fácilmente.
                        # Lo mejor es borrar el viejo y crear el nuevo, o simplemente devolver el viejo.
                        db.delete(existing_email)
                        db.commit()
                        
                    # Si no existe, lo creamos con los datos del token
                    new_user = Usuario(
                        id=user_uuid, 
                        email=email,
                        password_hash="KEYCLOAK_MANAGED"
                    )
                    db.add(new_user)
                    db.commit()
                    db.refresh(new_user)
        
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar token: {str(e)}",
        )

def require_role(role_name: str):
    """
    Dependencia opcional para requerir un rol específico.
    """
    async def role_checker(user: dict = Depends(get_current_user)):
        roles = user.get("realm_access", {}).get("roles", [])
        if role_name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requiere el rol: {role_name}"
            )
        return user
    return role_checker
