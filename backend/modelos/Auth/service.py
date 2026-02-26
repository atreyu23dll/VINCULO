from sqlalchemy.orm import Session
from modelos.Usuarios.modelo import Usuario

def autenticar_usuario(db: Session, email: str, password: str):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return None
    # Por ahora compara directo (igual que como se guarda en create_usuario)
    if usuario.password_hash != password:
        return None
    return usuario
