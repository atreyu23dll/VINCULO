from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from modelos.Usuarios.modelo import Usuario
from auth import get_current_user, get_keycloak_admin
from pydantic import BaseModel, EmailStr
import uuid

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

class PushTokenSchema(BaseModel):
    push_token: str

class UbicacionSchema(BaseModel):
    latitud: float
    longitud: float

class RegistroSchema(BaseModel):
    email: EmailStr
    password: str
    nombre: str | None = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/me/push-token")
async def actualizar_push_token(
    payload: PushTokenSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = uuid.UUID(current_user["sub"])
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.push_token = payload.push_token
    db.commit()
    print(f"✅ Push Token guardado para usuario {user.email}")
    return {"status": "ok"}

@router.post("/me/ubicacion")
async def actualizar_ubicacion(
    payload: UbicacionSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = uuid.UUID(current_user["sub"])
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.ultima_latitud = payload.latitud
    user.ultima_longitud = payload.longitud
    db.commit()
    print(f"📍 Ubicación actualizada para {user.email}: {payload.latitud}, {payload.longitud}")
    return {"status": "ok"}

@router.post("/registro")
async def registrar_usuario(payload: RegistroSchema, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en Keycloak y lo sincroniza en la base de datos local.
    """
    try:
        admin = get_keycloak_admin()
        
        # Dividir el nombre completo para satisfacer los requerimientos del perfil de Keycloak
        partes_nombre = (payload.nombre or "Usuario").strip().split(" ", 1)
        first_name = partes_nombre[0]
        last_name = partes_nombre[1] if len(partes_nombre) > 1 else " " # Keycloak puede rechazar un string vacío puro, mejor un espacio o repetirlo
        if not last_name.strip():
            last_name = first_name # Fallback si solo puso un nombre

        # 1. Crear el usuario en Keycloak sin credenciales primero
        keycloak_id = admin.create_user({
            "email": payload.email,
            "username": payload.email,
            "enabled": True,
            "emailVerified": True,
            "firstName": first_name,
            "lastName": last_name,
            "requiredActions": []
        }, exist_ok=False)

        # 1.5 Asignar la contraseña explícitamente para asegurar que se guarde sin acciones requeridas
        admin.set_user_password(user_id=keycloak_id, password=payload.password, temporary=False)
        
        # 2. Crear el usuario en nuestra base de datos local
        # El ID que nos da Keycloak es el que usaremos como primary key
        nuevo_usuario = Usuario(
            id=uuid.UUID(keycloak_id),
            email=payload.email,
            nombre=payload.nombre,
            password_hash="KEYCLOAK_MANAGED"
        )
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        print(f"👤 Usuario sincronizado en DB local: {payload.email} ({keycloak_id})")
        
        return {"status": "ok", "mensaje": "Usuario registrado exitosamente", "id": keycloak_id}
    except Exception as e:
        # Manejar errores de Keycloak (ej: usuario ya existe)
        detail = str(e)
        if "409" in detail:
            detail = "El usuario ya existe"
        
        # Si falló la inserción en DB pero se creó en Keycloak, 
        # podríamos tener una inconsistencia, pero lo normal es que sea el revés.
        print(f"❌ Error en registro: {detail}")
        raise HTTPException(status_code=400, detail=detail)
