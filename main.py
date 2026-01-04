import sys
import os
import multiprocessing

# --- PARCHE PARA MODO INVISIBLE (--noconsole) ---
# Esto debe ir ANTES de cualquier otra importación o lógica
class NullWriter:
    def write(self, text):
        pass
    def flush(self):
        pass
    def isatty(self):
        return False

if sys.stdout is None:
    sys.stdout = NullWriter()
if sys.stderr is None:
    sys.stderr = NullWriter()
# ------------------------------------------------

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import employees, attendance

# Crear carpeta uploads si no existe
os.makedirs("uploads", exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Checador API AI")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir carpeta uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(employees.router)
app.include_router(attendance.router)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    # Ejecutamos con log_config=None y access_log=False para máximo silencio
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None, access_log=False)