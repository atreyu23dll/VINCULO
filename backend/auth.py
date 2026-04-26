import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from keycloak import KeycloakOpenID
from sqlalchemy.orm import Session
from database import get_db
from modelos.Usuarios.modelo import Usuario

# Configuración de Keycloak
# Usamos el nombre del servicio en Docker para la comunicación interna
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
REALM_NAME = os.getenv("KEYCLOAK_REALM", "Vinculo")
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "vinculo-app")

keycloak_openid = KeycloakOpenID(
    server_url=f"{KEYCLOAK_URL}/",
    client_id=CLIENT_ID,
    realm_name=REALM_NAME,
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
            db_user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            if not db_user:
                # Si no existe, lo creamos con los datos del token
                email = payload.get("email", f"{usuario_id}@keycloak.local")
                new_user = Usuario(
                    id=usuario_id, 
                    email=email,
                    password_hash="KEYCLOAK_MANAGED" # No necesitamos password local
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
