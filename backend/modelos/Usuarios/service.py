from sqlalchemy.orm import Session
from .modelo import Usuario
from .dto import UsuarioCreate, UsuarioUpdate
from uuid import UUID

def get_usuario(db: Session, usuario_id: UUID):
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def get_usuario_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Usuario).offset(skip).limit(limit).all()

def create_usuario(db: Session, usuario: UsuarioCreate):
    # Nota: En un entorno real, aquí deberías hashear la contraseña
    db_usuario = Usuario(
        email=usuario.email,
        password_hash=usuario.password, # Simplificado para este ejemplo
        push_token=usuario.push_token,
        ultima_latitud=usuario.ultima_latitud,
        ultima_longitud=usuario.ultima_longitud
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def update_usuario(db: Session, usuario_id: UUID, usuario_update: UsuarioUpdate):
    db_usuario = get_usuario(db, usuario_id)
    if db_usuario:
        update_data = usuario_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_usuario, key, value)
        db.commit()
        db.refresh(db_usuario)
    return db_usuario

def delete_usuario(db: Session, usuario_id: UUID):
    db_usuario = get_usuario(db, usuario_id)
    if db_usuario:
        db.delete(db_usuario)
        db.commit()
        return True
    return False
