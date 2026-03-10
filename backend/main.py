from fastapi import FastAPI
from modelos.Auth.routes import router as auth_router
from modelos.Usuarios.routes import router as usuarios_router
from modelos.Deseos.routes import router as deseos_router
from modelos.UbicacionesDeseo.routes import router as ubicaciones_router
from modelos.Radar.routes import router as radar_router

app = FastAPI(title="Vinculo API")

app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(deseos_router)
app.include_router(ubicaciones_router)
app.include_router(radar_router)

@app.get("/")
def read_root():
    return {"mensaje": "Hola, el backend de Vinculo está vivo"}