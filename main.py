import uvicorn
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import employees, attendance

# Crear carpeta uploads si no existe
os.makedirs("uploads", exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Checador API AI")

# CORS: Vital para que Flutter (que corre en otro puerto en dev) pueda conectar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción puedes restringirlo, en dev déjalo así
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir la carpeta 'uploads' para que Flutter pueda ver las fotos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(employees.router)
app.include_router(attendance.router)

if __name__ == "__main__":
    # Recuerda usar ssl_keyfile si necesitas HTTPS, si no, déjalo simple para dev
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)