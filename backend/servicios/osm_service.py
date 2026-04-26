import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSMService:
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"

    def buscar_lugares_cercanos(self, tag_osm: str, lat: float, lon: float, radio: int = 3000):
        """
        Busca POIs en OpenStreetMap usando Overpass API.
        tag_osm: formato 'key:value' (ej: 'amenity:cafe')
        """
        try:
            key, value = tag_osm.split(':')
        except ValueError:
            logger.error(f"Formato de tag_osm inválido: {tag_osm}. Debe ser 'key:value'")
            return []

        # Construir consulta Overpass QL
        query = f"""
        [out:json][timeout:25];
        (
          node["{key}"="{value}"](around:{radio},{lat},{lon});
          way["{key}"="{value}"](around:{radio},{lat},{lon});
          relation["{key}"="{value}"](around:{radio},{lat},{lon});
        );
        out center;
        """

        logger.info(f"Consultando Overpass para {tag_osm} cerca de ({lat}, {lon}) en radio {radio}m")
        
        headers = {
            "User-Agent": "VinculoApp/1.0 (contacto: josmar@example.com)"
        }
        
        try:
            # Overpass API acepta el query en el parámetro 'data' via POST
            response = requests.post(self.overpass_url, data={'data': query}, headers=headers)
            
            if response.status_code == 406:
                logger.error("Error 406 de Overpass. Intentando con una petición simplificada...")
                # Algunos servidores de Overpass son más estrictos con el formato
                response = requests.get(self.overpass_url, params={'data': query}, headers=headers)
            
            response.raise_for_status()
            data = response.json()
            
            lugares = []
            for element in data.get('elements', []):
                l_lat = element.get('lat') or element.get('center', {}).get('lat')
                l_lon = element.get('lon') or element.get('center', {}).get('lon')
                
                if l_lat and l_lon:
                    lugares.append({
                        "osm_id": element.get('id'),
                        "nombre": element.get('tags', {}).get('name', 'Lugar sin nombre'),
                        "lat": l_lat,
                        "lon": l_lon,
                        "tipo": element.get('type')
                    })
            
            logger.info(f"Se encontraron {len(lugares)} lugares.")
            return lugares

        except Exception as e:
            logger.error(f"Error consultando Overpass: {e}")
            return []

# Instancia única
osm_service = OSMService()
