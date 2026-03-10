from sqlalchemy.orm import Session
from uuid import UUID
import requests
import time
from typing import List, Dict, Tuple
from modelos.Deseos.modelo import Deseo

# Diccionario en memoria para simular Caché Simple
# Formato: { uuid_usuario: (lat, lon) }
last_user_locations: Dict[UUID, Tuple[float, float]] = {}

def check_radar_matches(db: Session, usuario_id: UUID, lat: float, lon: float, radius: int) -> List[dict]:
    # 1. OPTIMIZACIÓN: Revisar si las coordenadas son idénticas a la última petición
    last_location = last_user_locations.get(usuario_id)
    if last_location and last_location == (lat, lon):
        # El usuario no se ha movido nada, saltar la verificación con la API externa
        print(f"📍 Radar Cache HIT para usuario {usuario_id}: Sin movimiento detectado.")
        return []

    # Actualizar la caché con la nueva ubicación
    last_user_locations[usuario_id] = (lat, lon)
    
    # 2. Buscar deseos activos del usuario ('pendiente' o 'buscando')
    deseos_activos = db.query(Deseo).filter(
        Deseo.usuario_id == usuario_id,
        Deseo.estado.in_(['pendiente', 'buscando'])
    ).all()

    if not deseos_activos:
        return []

    matches = []

    # 3. Consultar OpenStreetMap (Nominatim) por cada deseo
    # IMPORTANTE: Nominatim requiere User-Agent válido
    headers = {
        'User-Agent': 'VinculoApp/1.0 (david.rdz@example.com)'
    }

    for deseo in deseos_activos:
        # Usamos el tag configurado, o si no existe, el propio texto del deseo
        termino_busqueda = deseo.tag_osm if deseo.tag_osm else deseo.texto_original
        
        # Opcional: Acortar el término de búsqueda para Nominatim si es muy largo
        if len(termino_busqueda) > 30:
            termino_busqueda = termino_busqueda[:30]

        # Nominatim API
        url = "https://nominatim.openstreetmap.org/search"
        
        # Calcular Viewbox aproximado (1 grado ~= 111km)
        offset = radius / 111000.0
        min_lon = lon - offset
        max_lon = lon + offset
        min_lat = lat - offset
        max_lat = lat + offset
        viewbox = f"{min_lon},{min_lat},{max_lon},{max_lat}"

        params = {
            'q': termino_busqueda,
            'format': 'json',
            'limit': 3, # Nos interesan los más cercanos/relevantes
            'viewbox': viewbox,
            'bounded': 1
        }

        try:
            print(f"🌍 Consultando OSM para el deseo: {termino_busqueda} a radio de {radius}m...")
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                resultados = response.json()
                if resultados:
                    for resultado in resultados:
                        matches.append({
                            "lugar_nombre": resultado.get('display_name', 'Lugar Desconocido'),
                            "deseo_id": deseo.id,
                            "deseo_texto": deseo.texto_original,
                            "lat": float(resultado.get('lat', 0)),
                            "lon": float(resultado.get('lon', 0))
                        })
                    
        except Exception as e:
            print(f"❌ Error conectando a Nominatim: {e}")
            
        # Respetar límite estricto de Nominatim (1 req/seg)
        time.sleep(1.2)

    return matches
