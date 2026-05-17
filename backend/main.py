from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from modelos.Usuarios.routes import router as usuarios_router
from modelos.Deseos.routes import router as deseos_router
from modelos.UbicacionesDeseo.routes import router as ubicaciones_router
from modelos.Notificaciones.routes import router as notificaciones_router
# Importamos modelos para que el sistema cree las tablas
from modelos.Notificaciones.modelo import Notificacion
from modelos.Coordenadas.modelo import Coordenada
from auth import get_current_user
from init_db import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Esto se ejecutará cada vez que el servidor arranque
    init_db()
    yield

app = FastAPI(title="Vinculo API", lifespan=lifespan)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción deberías restringir esto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios_router)
app.include_router(deseos_router)
app.include_router(ubicaciones_router)
app.include_router(notificaciones_router)

@app.get("/")
def read_root():
    return {"mensaje": "Hola, el backend de Vinculo está vivo"}

@app.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    return {"user": user}
