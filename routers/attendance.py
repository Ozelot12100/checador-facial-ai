from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime, timedelta
import uuid
import os
from io import BytesIO
import database
import models
import schemas
from services.biometric import BiometricService

router = APIRouter(
    prefix="/api/attendance",
    tags=["Attendance"]
)

get_db = database.get_db

@router.post("/check-in", response_model=schemas.CheckInResponse)
async def check_in(file: UploadFile = File(...), db: Session = Depends(get_db)):
    
    # 1. Leer los bytes de la imagen (para usarla en IA y luego guardarla)
    file_bytes = await file.read()

    # 2. IA: Convertir foto a vector
    # Usamos BytesIO porque face_recognition espera un objeto tipo archivo
    incoming_vector = BiometricService.vector_from_image(BytesIO(file_bytes))

    if not incoming_vector:
        return schemas.CheckInResponse(
            success=False,
            message="No se detectó rostro en la cámara",
            time=datetime.now().strftime("%I:%M %p")
        )

    # 3. Buscar coincidencia en BD
    biometric_service = BiometricService(db)
    employee = biometric_service.find_best_match(incoming_vector)

    if not employee:
        return schemas.CheckInResponse(
            success=False,
            message="Empleado no reconocido",
            time=datetime.now().strftime("%I:%M %p")
        )

    # 4. Lógica de Negocio (Entrada/Salida - 12h)
    last_record = db.query(models.AttendanceRecord)\
        .filter(models.AttendanceRecord.employee_id == employee.id)\
        .order_by(desc(models.AttendanceRecord.timestamp_utc))\
        .first()

    new_type = 0 # CheckIn
    
    match_score = BiometricService.calculate_distance(incoming_vector, employee.face_vector)

    if last_record:
        hours_since = (datetime.utcnow() - last_record.timestamp_utc).total_seconds() / 3600
        if last_record.type == 0 and hours_since < 12:
            new_type = 1 # CheckOut

    # 5. Guardar la FOTO en disco (NUEVO)
    # Generamos un nombre único con UUID para evitar colisiones
    filename = f"{uuid.uuid4()}.jpg"
    
    # Aseguramos que la carpeta uploads exista (por seguridad, aunque main.py ya lo hace)
    os.makedirs("uploads", exist_ok=True)
    
    file_path_disk = os.path.join("uploads", filename)
    
    # Escribimos el archivo físico
    with open(file_path_disk, "wb") as f:
        f.write(file_bytes)
    
    # Ruta relativa para la URL (usamos '/' para que sea compatible con web)
    photo_url = f"uploads/{filename}"

    # 6. Crear registro en BD
    new_record = models.AttendanceRecord(
        employee_id=employee.id,
        timestamp_utc=datetime.utcnow(),
        local_time=datetime.now(),
        type=new_type,
        match_score=match_score,
        photo_path=photo_url # <--- Campo nuevo para el Admin
    )
    
    db.add(new_record)
    db.commit()

    # 7. Respuesta
    action_msg = "Bienvenido" if new_type == 0 else "Hasta luego"
    first_name = employee.full_name.split(" ")[0]
    
    return schemas.CheckInResponse(
        success=True,
        message=f"{action_msg} {first_name}",
        employee_name=employee.full_name,
        employee_code=employee.code,
        time=new_record.local_time.strftime("%I:%M %p")
    )

@router.get("/history/{employee_id}", response_model=List[schemas.AttendanceRecordResponse])
def get_history(employee_id: str, db: Session = Depends(get_db)):
    return db.query(models.AttendanceRecord)\
        .filter(models.AttendanceRecord.employee_id == employee_id)\
        .order_by(desc(models.AttendanceRecord.timestamp_utc))\
        .limit(50)\
        .all()

@router.get("/today", response_model=List[schemas.AttendanceRecordResponse])
def get_today_records(db: Session = Depends(get_db)):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    return db.query(models.AttendanceRecord)\
        .filter(models.AttendanceRecord.local_time >= today, models.AttendanceRecord.local_time < tomorrow)\
        .order_by(desc(models.AttendanceRecord.timestamp_utc))\
        .all()