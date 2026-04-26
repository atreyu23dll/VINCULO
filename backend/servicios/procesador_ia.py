import logging
from transformers import pipeline
import torch
from database import SessionLocal
from modelos.TagsOSM.modelo import TagOSM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mapeo de categorías para búsqueda jerárquica
CATEGORIAS = {
    "Alimentación y Bebidas": ["panadería", "pastelería", "cafetería", "restaurante", "comida rápida", "heladería", "bar", "pub", "supermercado", "tienda de conveniencia", "frutería", "carnicería", "pescadería", "licorería", "dulces"],
    "Salud y Bienestar": ["farmacia", "hospital", "clínica", "médico", "dentista", "veterinaria", "óptica", "gimnasio", "deportes", "spa", "masajes"],
    "Servicios y Finanzas": ["banco", "cajero", "cambio de moneda", "correos", "policía", "bomberos", "ayuntamiento", "juzgado", "comunitario", "baños públicos", "agua potable", "reciclaje"],
    "Compras y Moda": ["ropa", "zapatería", "joyería", "centro comercial", "perfumería", "cosméticos", "boutique", "regalos", "juguetería", "librería", "papelería"],
    "Hogar y Tecnología": ["electrónica", "celulares", "ferretería", "muebles", "jardín", "mascotas", "lavandería", "tintorería"],
    "Automotriz": ["gasolinera", "taller", "mecánico", "lavado de autos", "estacionamiento", "repuestos"],
    "Entretenimiento y Turismo": ["cine", "teatro", "museo", "galería", "biblioteca", "parque", "zoológico", "hotel", "hostal", "motel", "turismo", "mirador", "discoteca", "casino"],
    "Belleza y Oficios": ["peluquería", "barbería", "salón de belleza", "cerrajería", "sastrería", "reparación de calzado", "floristería"]
}

class ProcesadorIA:
    def __init__(self):
        self.model_name = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
        self.classifier = None
        self.etiquetas_cache = {}
        self.mapeo_categoria = {}

    def _cargar_modelo(self):
        if self.classifier is not None: return
        logger.info("Cargando modelo IA optimizado...")
        device = 0 if torch.cuda.is_available() else -1
        try:
            self.classifier = pipeline("zero-shot-classification", model=self.model_name, device=device)
            logger.info("Modelo cargado.")
        except Exception as e:
            logger.error(f"Error carga modelo: {e}")

    def _cargar_etiquetas_desde_db(self):
        db = SessionLocal()
        try:
            tags = db.query(TagOSM).all()
            self.etiquetas_cache = {t.nombre_humano: f"{t.llave_osm}:{t.valor_osm}" for t in tags}
            
            # Clasificar etiquetas en categorías para búsqueda rápida
            for nombre in self.etiquetas_cache.keys():
                encontrado = False
                for cat, keywords in CATEGORIAS.items():
                    if any(kw in nombre.lower() for kw in keywords):
                        if cat not in self.mapeo_categoria: self.mapeo_categoria[cat] = []
                        self.mapeo_categoria[cat].append(nombre)
                        encontrado = True
                        break
                if not encontrado:
                    if "Otros" not in self.mapeo_categoria: self.mapeo_categoria["Otros"] = []
                    self.mapeo_categoria["Otros"].append(nombre)
            
            logger.info(f"Cache optimizada: {len(self.etiquetas_cache)} etiquetas en {len(self.mapeo_categoria)} categorías.")
        except Exception as e:
            logger.error(f"Error DB tags: {e}")
        finally:
            db.close()

    def procesar_deseo(self, texto: str) -> str:
        self._cargar_modelo()
        if not self.classifier: return None
        if not self.etiquetas_cache: self._cargar_etiquetas_desde_db()

        # PASO 1: Clasificación de Categoría (Rápido)
        logger.info(f"Paso 1: Clasificando categoría para '{texto}'")
        cat_labels = list(self.mapeo_categoria.keys())
        res_cat = self.classifier(texto, cat_labels, multi_label=False)
        mejor_cat = res_cat['labels'][0]
        logger.info(f"Categoría ganadora: {mejor_cat}")

        # PASO 2: Clasificación Detallada (Solo dentro de la categoría ganadora)
        etiquetas_candidatas = self.mapeo_categoria[mejor_cat]
        logger.info(f"Paso 2: Buscando detalle entre {len(etiquetas_candidatas)} etiquetas")
        
        res_det = self.classifier(
            texto, 
            etiquetas_candidatas, 
            multi_label=False,
            hypothesis_template="Este deseo se refiere a {}."
        )
        
        mejor_etiqueta = res_det['labels'][0]
        osm_tag = self.etiquetas_cache[mejor_etiqueta]
        logger.info(f"Resultado final: {mejor_etiqueta} ({osm_tag})")
        
        return osm_tag

procesador_ia = ProcesadorIA()
