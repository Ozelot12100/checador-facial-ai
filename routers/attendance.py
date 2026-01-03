from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, joinedload
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

    # 4. Lógica de Negocio con validación de cooldown
    last_record = db.query(models.AttendanceRecord)\
        .filter(models.AttendanceRecord.employee_id == employee.id)\
        .order_by(desc(models.AttendanceRecord.timestamp_utc))\
        .first()

    new_type = 0 # CheckIn por defecto
    
    match_score = BiometricService.calculate_distance(incoming_vector, employee.face_vector)

    if last_record:
        time_diff = datetime.utcnow() - last_record.timestamp_utc
        seconds_since = time_diff.total_seconds()
        minutes_since = seconds_since / 60
        hours_since = seconds_since / 3600
        
        # ⚡ REGLA 1: ANTI-REBOTE (Cooldown Global de 60 segundos)
        # Si han pasado menos de 60 segundos, NO guardar en BD
        # Retornar éxito para no confundir al usuario con error rojo
        if seconds_since < 60:
            first_name = employee.full_name.split(" ")[0]
            last_action = "entrada" if last_record.type == 0 else "salida"
            return schemas.CheckInResponse(
                success=True,
                message=f"✓ Ya registraste tu {last_action}, {first_name}",
                employee_name=employee.full_name,
                employee_code=employee.code,
                time=last_record.local_time.strftime("%I:%M %p")
            )
        
        # 🔄 REGLA 2: JORNADA EXTENDIDA (Smart Toggle con 16 horas)
        # Si último registro fue ENTRADA (type 0)
        if last_record.type == 0:
            # Si han pasado menos de 16 horas → SALIDA
            if hours_since < 16:
                new_type = 1  # Marcar SALIDA
            else:
                # Si han pasado más de 16 horas → Nueva ENTRADA (reseteo de jornada)
                new_type = 0
                
        # Si último registro fue SALIDA (type 1)
        elif last_record.type == 1:
            # Siempre será ENTRADA después de una SALIDA
            # (El cooldown de 60 segundos ya previene duplicados)
            new_type = 0

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
def get_today_records(
    start_date: str = None,
    end_date: str = None,
    employee_id: str = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene registros de asistencia con filtros opcionales.
    - start_date: formato YYYY-MM-DD (ej: 2026-01-01)
    - end_date: formato YYYY-MM-DD (ej: 2026-01-05)
    - employee_id: UUID del empleado para filtrar por empleado específico
    Si no se proporcionan fechas, retorna solo el día de hoy.
    """
    # Si no se especifican fechas, usar día de hoy por defecto
    if not start_date:
        start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    else:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            # Si no hay end_date, usar el mismo día que start_date
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            else:
                end = start + timedelta(days=1)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Formato de fecha inválido. Usa YYYY-MM-DD (ej: 2026-01-01)"
            )
    
    # Construir query con filtros
    query = db.query(models.AttendanceRecord)\
        .options(joinedload(models.AttendanceRecord.employee))\
        .filter(models.AttendanceRecord.local_time >= start, models.AttendanceRecord.local_time < end)
    
    # Filtrar por empleado si se especifica
    if employee_id:
        query = query.filter(models.AttendanceRecord.employee_id == employee_id)
    
    records = query.order_by(desc(models.AttendanceRecord.timestamp_utc)).all()
    
    # Construir respuesta enriquecida con datos del empleado
    result = []
    for record in records:
        result.append({
            "id": str(record.id),
            "timestamp_utc": record.timestamp_utc,
            "type": record.type,
            "match_score": record.match_score,
            "employee_id": str(record.employee_id),
            "employee_name": record.employee.full_name,
            "employee_code": record.employee.code,
            "photo_path": record.photo_path
        })
    
    return result