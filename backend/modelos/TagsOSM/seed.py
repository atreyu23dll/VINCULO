from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from modelos.TagsOSM.modelo import TagOSM

# Lista maestra de etiquetas para ser usada en semillas y migraciones
TAGS_DATA = [
    # ALIMENTACIÓN Y BEBIDAS
    {"nombre_humano": "panadería o pastelería", "llave_osm": "shop", "valor_osm": "bakery"},
    {"nombre_humano": "cafetería", "llave_osm": "amenity", "valor_osm": "cafe"},
    {"nombre_humano": "restaurante", "llave_osm": "amenity", "valor_osm": "restaurant"},
    {"nombre_humano": "comida rápida", "llave_osm": "amenity", "valor_osm": "fast_food"},
    {"nombre_humano": "heladería", "llave_osm": "amenity", "valor_osm": "ice_cream"},
    {"nombre_humano": "bar o taberna", "llave_osm": "amenity", "valor_osm": "bar"},
    {"nombre_humano": "pub", "llave_osm": "amenity", "valor_osm": "pub"},
    {"nombre_humano": "supermercado", "llave_osm": "shop", "valor_osm": "supermarket"},
    {"nombre_humano": "tienda de conveniencia", "llave_osm": "shop", "valor_osm": "convenience"},
    {"nombre_humano": "frutería y verdulería", "llave_osm": "shop", "valor_osm": "greengrocer"},
    {"nombre_humano": "carnicería", "llave_osm": "shop", "valor_osm": "butcher"},
    {"nombre_humano": "pescadería", "llave_osm": "shop", "valor_osm": "seafood"},
    {"nombre_humano": "tienda de vinos y licores", "llave_osm": "shop", "valor_osm": "alcohol"},
    {"nombre_humano": "confitería o dulces", "llave_osm": "shop", "valor_osm": "confectionery"},
    
    # SALUD Y BIENESTAR
    {"nombre_humano": "farmacia", "llave_osm": "amenity", "valor_osm": "pharmacy"},
    {"nombre_humano": "hospital o clínica", "llave_osm": "amenity", "valor_osm": "hospital"},
    {"nombre_humano": "consultorio médico", "llave_osm": "amenity", "valor_osm": "doctors"},
    {"nombre_humano": "dentista", "llave_osm": "amenity", "valor_osm": "dentist"},
    {"nombre_humano": "veterinaria", "llave_osm": "amenity", "valor_osm": "veterinary"},
    {"nombre_humano": "óptica", "llave_osm": "shop", "valor_osm": "optician"},
    {"nombre_humano": "gimnasio", "llave_osm": "leisure", "valor_osm": "fitness_centre"},
    {"nombre_humano": "centro deportivo", "llave_osm": "leisure", "valor_osm": "sports_centre"},
    {"nombre_humano": "spa o centro de masajes", "llave_osm": "leisure", "valor_osm": "spa"},
    
    # SERVICIOS FINANCIEROS
    {"nombre_humano": "banco", "llave_osm": "amenity", "valor_osm": "bank"},
    {"nombre_humano": "cajero automático", "llave_osm": "amenity", "valor_osm": "atm"},
    {"nombre_humano": "casa de cambio", "llave_osm": "amenity", "valor_osm": "bureau_de_change"},
    
    # COMPRAS Y MODA
    {"nombre_humano": "tienda de ropa", "llave_osm": "shop", "valor_osm": "clothes"},
    {"nombre_humano": "zapatería", "llave_osm": "shop", "valor_osm": "shoes"},
    {"nombre_humano": "joyería", "llave_osm": "shop", "valor_osm": "jewelry"},
    {"nombre_humano": "centro comercial", "llave_osm": "shop", "valor_osm": "mall"},
    {"nombre_humano": "grandes almacenes", "llave_osm": "shop", "valor_osm": "department_store"},
    {"nombre_humano": "perfumería", "llave_osm": "shop", "valor_osm": "perfumery"},
    {"nombre_humano": "tienda de cosméticos", "llave_osm": "shop", "valor_osm": "cosmetics"},
    {"nombre_humano": "boutique", "llave_osm": "shop", "valor_osm": "boutique"},
    
    # HOGAR Y TECNOLOGÍA
    {"nombre_humano": "tienda de electrónica", "llave_osm": "shop", "valor_osm": "electronics"},
    {"nombre_humano": "tienda de celulares", "llave_osm": "shop", "valor_osm": "mobile_phone"},
    {"nombre_humano": "ferretería", "llave_osm": "shop", "valor_osm": "hardware"},
    {"nombre_humano": "tienda de muebles", "llave_osm": "shop", "valor_osm": "furniture"},
    {"nombre_humano": "tienda de artículos para el hogar", "llave_osm": "shop", "valor_osm": "houseware"},
    {"nombre_humano": "vivero o jardín", "llave_osm": "shop", "valor_osm": "garden_centre"},
    {"nombre_humano": "tienda de mascotas", "llave_osm": "shop", "valor_osm": "pet"},
    {"nombre_humano": "librería", "llave_osm": "shop", "valor_osm": "books"},
    {"nombre_humano": "papelería", "llave_osm": "shop", "valor_osm": "stationery"},
    {"nombre_humano": "juguetería", "llave_osm": "shop", "valor_osm": "toys"},
    {"nombre_humano": "tienda de regalos", "llave_osm": "shop", "valor_osm": "gift"},
    
    # AUTOMOTRIZ
    {"nombre_humano": "gasolinera", "llave_osm": "amenity", "valor_osm": "fuel"},
    {"nombre_humano": "taller mecánico", "llave_osm": "shop", "valor_osm": "car_repair"},
    {"nombre_humano": "lavado de autos", "llave_osm": "amenity", "valor_osm": "car_wash"},
    {"nombre_humano": "estacionamiento", "llave_osm": "amenity", "valor_osm": "parking"},
    {"nombre_humano": "tienda de autopartes", "llave_osm": "shop", "valor_osm": "car_parts"},
    
    # ENTRETENIMIENTO Y CULTURA
    {"nombre_humano": "cine", "llave_osm": "amenity", "valor_osm": "cinema"},
    {"nombre_humano": "teatro", "llave_osm": "amenity", "valor_osm": "theatre"},
    {"nombre_humano": "museo", "llave_osm": "tourism", "valor_osm": "museum"},
    {"nombre_humano": "galería de arte", "llave_osm": "tourism", "valor_osm": "gallery"},
    {"nombre_humano": "biblioteca", "llave_osm": "amenity", "valor_osm": "library"},
    {"nombre_humano": "parque", "llave_osm": "leisure", "valor_osm": "park"},
    {"nombre_humano": "zoológico", "llave_osm": "tourism", "valor_osm": "zoo"},
    {"nombre_humano": "parque de atracciones", "llave_osm": "tourism", "valor_osm": "theme_park"},
    {"nombre_humano": "club nocturno o discoteca", "llave_osm": "amenity", "valor_osm": "nightclub"},
    {"nombre_humano": "casino", "llave_osm": "amenity", "valor_osm": "casino"},
    
    # SERVICIOS PÚBLICOS Y EDUCACIÓN
    {"nombre_humano": "escuela", "llave_osm": "amenity", "valor_osm": "school"},
    {"nombre_humano": "universidad", "llave_osm": "amenity", "valor_osm": "university"},
    {"nombre_humano": "oficina de correos", "llave_osm": "amenity", "valor_osm": "post_office"},
    {"nombre_humano": "estación de policía", "llave_osm": "amenity", "valor_osm": "police"},
    {"nombre_humano": "estación de bomberos", "llave_osm": "amenity", "valor_osm": "fire_station"},
    {"nombre_humano": "ayuntamiento", "llave_osm": "amenity", "valor_osm": "townhall"},
    {"nombre_humano": "juzgado", "llave_osm": "amenity", "valor_osm": "courthouse"},
    {"nombre_humano": "centro comunitario", "llave_osm": "amenity", "valor_osm": "community_centre"},
    
    # TURISMO Y ALOJAMIENTO
    {"nombre_humano": "hotel", "llave_osm": "tourism", "valor_osm": "hotel"},
    {"nombre_humano": "hostal", "llave_osm": "tourism", "valor_osm": "hostel"},
    {"nombre_humano": "motel", "llave_osm": "tourism", "valor_osm": "motel"},
    {"nombre_humano": "información turística", "llave_osm": "tourism", "valor_osm": "information"},
    {"nombre_humano": "mirador", "llave_osm": "tourism", "valor_osm": "viewpoint"},
    
    # BELLEZA Y CUIDADO PERSONAL
    {"nombre_humano": "peluquería", "llave_osm": "shop", "valor_osm": "hairdresser"},
    {"nombre_humano": "barbería", "llave_osm": "shop", "valor_osm": "barber"},
    {"nombre_humano": "salón de belleza", "llave_osm": "shop", "valor_osm": "beauty"},
    {"nombre_humano": "lavandería", "llave_osm": "shop", "valor_osm": "laundry"},
    {"nombre_humano": "tintorería", "llave_osm": "shop", "valor_osm": "dry_cleaning"},
    
    # OFICIOS Y OTROS
    {"nombre_humano": "cerrajería", "llave_osm": "shop", "valor_osm": "locksmith"},
    {"nombre_humano": "sastrería", "llave_osm": "shop", "valor_osm": "tailor"},
    {"nombre_humano": "reparación de calzado", "llave_osm": "shop", "valor_osm": "shoe_repair"},
    {"nombre_humano": "floristería", "llave_osm": "shop", "valor_osm": "florist"},
    {"nombre_humano": "estanco", "llave_osm": "shop", "valor_osm": "tobacco"},
    {"nombre_humano": "agencia de viajes", "llave_osm": "shop", "valor_osm": "travel_agency"},
    {"nombre_humano": "tienda de deportes", "llave_osm": "shop", "valor_osm": "sports"},
    {"nombre_humano": "tienda de bicicletas", "llave_osm": "shop", "valor_osm": "bicycle"},
    {"nombre_humano": "tienda de música", "llave_osm": "shop", "valor_osm": "musical_instrument"},
    {"nombre_humano": "casa de empeño", "llave_osm": "shop", "valor_osm": "pawnshop"},
    {"nombre_humano": "funeraria", "llave_osm": "amenity", "valor_osm": "funeral_hall"},
    {"nombre_humano": "iglesia o templo", "llave_osm": "amenity", "valor_osm": "place_of_worship"},
    {"nombre_humano": "baños públicos", "llave_osm": "amenity", "valor_osm": "toilets"},
    {"nombre_humano": "agua potable", "llave_osm": "amenity", "valor_osm": "drinking_water"},
    {"nombre_humano": "punto de reciclaje", "llave_osm": "amenity", "valor_osm": "recycling"},
]

def seed_tags():
    db = SessionLocal()
    print(f"Iniciando sembrado de {len(TAGS_DATA)} etiquetas OSM...")
    
    try:
        for data in TAGS_DATA:
            existente = db.query(TagOSM).filter(TagOSM.nombre_humano == data["nombre_humano"]).first()
            if not existente:
                nuevo_tag = TagOSM(**data)
                db.add(nuevo_tag)
                print(f" -> Añadido: {data['nombre_humano']}")
            else:
                existente.llave_osm = data["llave_osm"]
                existente.valor_osm = data["valor_osm"]
                print(f" -> Actualizado: {data['nombre_humano']}")
        
        db.commit()
        print("¡Sembrado completado con éxito!")
    except Exception as e:
        print(f"Error durante el sembrado: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    Base.metadata.create_all(bind=engine)
    seed_tags()
