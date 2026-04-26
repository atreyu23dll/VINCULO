from database import engine, Base, SessionLocal
from modelos.TagsOSM.seed import seed_tags
import logging

# IMPORTANTE: Importar todos los modelos para que Base los registre
from modelos.Usuarios.modelo import Usuario
from modelos.Deseos.modelo import Deseo
from modelos.UbicacionesDeseo.modelo import UbicacionDeseo
from modelos.Coordenadas.modelo import Coordenada
from modelos.Notificaciones.modelo import Notificacion
from modelos.TagsOSM.modelo import TagOSM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("🚀 Iniciando base de datos y creando tablas...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Todas las tablas (Deseos, Ubicaciones, Coordenadas, Notificaciones) verificadas.")

    logger.info("🌱 Verificando semillas de Tags OSM...")
    try:
        seed_tags()
        logger.info("✅ Sembrado de Tags completado.")
    except Exception as e:
        logger.error(f"❌ Error durante el sembrado: {e}")

if __name__ == "__main__":
    init_db()
