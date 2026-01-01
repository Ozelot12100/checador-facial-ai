import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import employees, attendance

# Crea las tablas en la base de datos si no existen (igual que db.Database.EnsureCreated() en C#)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Checador API Python",
    description="API de asistencia con reconocimiento facial migrada a Python",
    version="1.0.0"
)

# Configuración CORS: Vital para acceso local desde otros dispositivos/frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite todas las conexiones (seguro para red local)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar las rutas
app.include_router(employees.router)
app.include_router(attendance.router)

@app.get("/")
def read_root():
    return {"message": "Sistema Checador Python Activo", "docs_url": "/docs"}

if __name__ == "__main__":
    # Configuración para red local:
    # host="0.0.0.0" hace que el servidor escuche en TODAS las IPs de tu PC,
    # permitiendo que tu celular se conecte.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)