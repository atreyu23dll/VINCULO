from database import SessionLocal, engine, Base
from modelos.Deseos import service, dto
from modelos.Usuarios.modelo import Usuario
from modelos.UbicacionesDeseo.modelo import UbicacionDeseo
import uuid

def test_ciclo_completo():
    db = SessionLocal()
    
    # 1. Usuario de prueba
    test_user_id = "00000000-0000-0000-0000-000000000001"
    
    # 2. Datos del deseo y ubicación (CDMX, Centro Histórico)
    # 19.4326, -99.1332
    deseo_texto = "Quiero un café americano"
    lat = 19.4326
    lon = -99.1332

    print(f"\n--- TEST CICLO COMPLETO: '{deseo_texto}' ---")
    
    # Creamos el deseo con coordenadas
    nuevo_deseo = dto.DeseoCreate(
        usuario_id=test_user_id,
        texto_original=deseo_texto,
        radio_busqueda_metros=1000, # 1km a la redonda
        latitud_usuario=lat,
        longitud_usuario=lon
    )
    
    # El servicio hará la IA + OSM
    resultado = service.create_deseo(db, nuevo_deseo)
    
    print(f"\n1. IA: Tag detectado: {resultado.tag_osm}")
    
    # 3. Verificar si se guardaron ubicaciones
    ubicaciones = db.query(UbicacionDeseo).filter(UbicacionDeseo.deseo_id == resultado.id).all()
    
    print(f"2. OSM: Se encontraron y guardaron {len(ubicaciones)} locales cercanos.")
    
    for i, u in enumerate(ubicaciones[:5]): # Mostrar los primeros 5
        print(f"   -> [{i+1}] {u.nombre_lugar} (OSM ID: {u.osm_id})")

    if not ubicaciones:
        print("   (!) No se encontraron locales en ese radio con ese tag.")

    db.close()

if __name__ == "__main__":
    test_ciclo_completo()
