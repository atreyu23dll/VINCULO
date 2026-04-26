import os
import time
import requests
from celery import Celery
from sqlalchemy.orm import Session
from database import SessionLocal
from modelos.Deseos.modelo import Deseo
from modelos.UbicacionesDeseo.modelo import UbicacionDeseo
from modelos.Notificaciones.modelo import Notificacion
from modelos.Coordenadas.modelo import Coordenada
from modelos.Usuarios.modelo import Usuario
from servicios.procesador_ia import procesador_ia
from servicios.osm_service import osm_service
from geoalchemy2.elements import WKTElement
from sqlalchemy import func as sql_func

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

# Configuración de tareas programadas (Beat)
celery_app.conf.beat_schedule = {
    "verificar-proximidad-cada-minuto": {
        "task": "verificar_proximidad_notificaciones",
        "schedule": 60.0, # Cada 60 segundos (1 minuto)
    },
}
celery_app.conf.timezone = 'UTC'

def enviar_push_expo(expo_token, titulo, mensaje):
    """Envía una notificación real al celular a través de Expo"""
    try:
        url = "https://exp.host/--/api/v2/push/send"
        payload = {
            "to": expo_token,
            "title": titulo,
            "body": mensaje,
            "sound": "default",
            "priority": "high",
            "data": {"click_action": "FLUTTER_NOTIFICATION_CLICK"}
        }
        res = requests.post(url, json=payload)
        print(f"📡 Resultado Push Expo: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Error enviando Push: {e}")

@celery_app.task(name="procesar_deseo_completo")
def procesar_deseo_completo(deseo_id: str):
    db: Session = SessionLocal()
    db_deseo = None
    try:
        db_deseo = db.query(Deseo).filter(Deseo.id == deseo_id).first()
        if not db_deseo: return "Deseo no encontrado"
        
        db_deseo.estado = "analizando"
        db.commit()
        
        tag_sugerido = procesador_ia.procesar_deseo(db_deseo.texto_original)
        db_deseo.tag_osm = tag_sugerido
        db_deseo.estado = "buscando"
        db.commit()
        
        if db_deseo.tag_osm:
            locales = osm_service.buscar_lugares_cercanos(
                tag_osm=db_deseo.tag_osm,
                lat=db_deseo.latitud_usuario,
                lon=db_deseo.longitud_usuario,
                radio=db_deseo.radio_busqueda_metros
            )
            for locale in locales:
                nueva_ubi = UbicacionDeseo(
                    deseo_id=db_deseo.id,
                    osm_id=locale['osm_id'],
                    nombre_lugar=locale['nombre'],
                    ubicacion=WKTElement(f"POINT({locale['lon']} {locale['lat']})", srid=4326)
                )
                db.add(nueva_ubi)
            
        db_deseo.estado = "completado"
        db.commit()
        return f"Deseo {deseo_id} procesado"
    finally:
        db.close()

@celery_app.task(name="verificar_proximidad_notificaciones")
def verificar_proximidad_notificaciones():
    db: Session = SessionLocal()
    try:
        # Buscamos a todos los usuarios que tengan una ubicación registrada
        usuarios = db.query(Usuario).filter(Usuario.ultima_latitud != None, Usuario.ultima_longitud != None).all()
        notificaciones_enviadas = 0

        for usuario in usuarios:
            distancia_max = 500 # 500 metros
            punto_usuario = WKTElement(f"POINT({usuario.ultima_longitud} {usuario.ultima_latitud})", srid=4326)

            # Buscamos lugares cercanos para ESTE usuario específico
            cercanos = db.query(UbicacionDeseo).join(Deseo).filter(
                Deseo.usuario_id == usuario.id,
                UbicacionDeseo.ya_notificado == False,
                sql_func.ST_DistanceSphere(UbicacionDeseo.ubicacion, punto_usuario) <= distancia_max
            ).all()

            for ubi in cercanos:
                # Doble verificación para evitar duplicados en segundos
                db.refresh(ubi)
                if ubi.ya_notificado:
                    continue

                distancia = db.scalar(sql_func.ST_DistanceSphere(ubi.ubicacion, punto_usuario))
                mensaje = f"¡Vínculo detectado! Hay un {ubi.nombre_lugar}, a {int(distancia)} metros. ¿Listo para cumplir tu deseo?"
                
                # 1. Guardar en DB
                nueva_notif = Notificacion(usuario_id=usuario.id, mensaje=mensaje)
                db.add(nueva_notif)
                
                # 2. Marcar como notificado INMEDIATAMENTE
                ubi.ya_notificado = True
                ubi.fecha_notificacion = sql_func.now()
                db.commit() # Commit inmediato para que otra tarea no lo vea

                # 3. ENVIAR PUSH REAL
                if usuario.push_token:
                    enviar_push_expo(usuario.push_token, "¡VÍNCULO CERCANO!", mensaje)
                
                notificaciones_enviadas += 1
            
        return f"Proximidad verificada. {notificaciones_enviadas} notificaciones enviadas."
    finally:
        db.close()
