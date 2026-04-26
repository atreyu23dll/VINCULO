from database import SessionLocal, engine, Base
from modelos.Deseos import service, dto
from modelos.Usuarios.modelo import Usuario
import uuid

def test_reconocimiento():
    db = SessionLocal()
    
    # 1. Asegurar que exista un usuario de prueba
    test_user_id = "00000000-0000-0000-0000-000000000001"
    user = db.query(Usuario).filter(Usuario.id == test_user_id).first()
    if not user:
        user = Usuario(
            id=test_user_id,
            email="test@vinculo.com",
            password_hash="fake_hash"
        )
        db.add(user)
        db.commit()
        print(f"Usuario de prueba creado: {test_user_id}")

    # 2. Casos de prueba
    deseos_a_probar = [
        "Quiero comprar un pastel de chocolate",
        "Me urge una medicina para el estomago",
        "Tengo hambre de una hamburguesa",
        "Se me poncho una llanta, necesito un taller",
        "Quiero un libro de ciencia ficcion"
    ]

    print("\n--- INICIANDO PRUEBA DE RECONOCIMIENTO CON IA ---")
    
    for texto in deseos_a_probar:
        print(f"\nProcesando: '{texto}'...")
        
        # Creamos el DTO de entrada (sin tag_osm, para que la IA lo deduzca)
        nuevo_deseo = dto.DeseoCreate(
            usuario_id=test_user_id,
            texto_original=texto,
            radio_busqueda_metros=3000,
            prioridad="media"
        )
        
        # Llamamos al servicio (aquí ocurre la magia de la IA)
        resultado = service.create_deseo(db, nuevo_deseo)
        
        print(f" -> RESULTADO:")
        print(f"    Texto Original: {resultado.texto_original}")
        print(f"    Tag Detectado : {resultado.tag_osm if resultado.tag_osm else 'No detectado'}")
        print(f"    ID Deseo      : {resultado.id}")

    db.close()

if __name__ == "__main__":
    # Aseguramos que las tablas existan
    Base.metadata.create_all(bind=engine)
    test_reconocimiento()
