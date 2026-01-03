from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
from io import BytesIO
import database
import models
import schemas
from services.biometric import BiometricService

router = APIRouter(
    prefix="/api/employees",
    tags=["Employees"]
)

get_db = database.get_db

@router.post("/", response_model=schemas.EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_employee(
    code: str = Form(...),
    full_name: str = Form(...),
    file: UploadFile = File(None),  # Opcional: permite actualizar sin cambiar foto
    employee_id: str = Form(None),  # ID del empleado a actualizar (None si es nuevo)
    db: Session = Depends(get_db)
):
    # Variables para foto y vector (se procesan solo si hay archivo nuevo)
    face_vector = None
    photo_url = None
    
    # 1. Si se envió una nueva foto, procesarla
    if file is not None:
        # Leer los bytes de la imagen (para IA y para guardar)
        file_bytes = await file.read()

        # 2. IA: Procesar imagen para obtener el vector facial
        # Usamos BytesIO porque la librería espera un objeto tipo archivo
        face_vector = BiometricService.vector_from_image(BytesIO(file_bytes))

        if not face_vector:
            raise HTTPException(
                status_code=400, 
                detail="No se detectó ningún rostro en la imagen. Intente con una foto más clara."
            )

        # 3. Guardar la FOTO DE PERFIL en disco
        # Usamos un prefijo 'profile_' para distinguirlas de las de asistencia
        filename = f"profile_{uuid.uuid4()}.jpg"
        
        # Asegurar que la carpeta exista
        os.makedirs("uploads", exist_ok=True)
        
        file_path_disk = os.path.join("uploads", filename)
        
        # Escribir el archivo
        with open(file_path_disk, "wb") as f:
            f.write(file_bytes)
            
        # Ruta relativa para la URL y la Base de Datos
        photo_url = f"uploads/{filename}"

    # 4. Lógica de Actualización o Creación
    existing_employee = None
    
    # Si se proporcionó employee_id, buscar por ID (actualización)
    if employee_id:
        existing_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    else:
        # Si no hay ID, buscar por código (para evitar duplicados)
        existing_employee = db.query(models.Employee).filter(models.Employee.code == code).first()
    
    if existing_employee:
        # Si ya existe, actualizamos sus datos
        existing_employee.full_name = full_name
        existing_employee.code = code  # Actualizar el código también
        existing_employee.is_active = True  # Reactivamos si estaba dado de baja
        
        # Solo actualizar foto y vector si se envió una nueva imagen
        if face_vector and photo_url:
            existing_employee.face_vector = face_vector
            existing_employee.photo_path = photo_url
        
        db.commit()
        db.refresh(existing_employee)
        return existing_employee

    # Si es nuevo, validar que se haya enviado foto (obligatoria para crear)
    if file is None:
        raise HTTPException(
            status_code=400,
            detail="La foto es obligatoria al registrar un nuevo empleado."
        )
    
    # Crear nuevo empleado
    new_employee = models.Employee(
        code=code,
        full_name=full_name,
        face_vector=face_vector,
        photo_path=photo_url
    )
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return new_employee

@router.get("/", response_model=List[schemas.EmployeeResponse])
def get_all_employees(db: Session = Depends(get_db)):
    # Retorna solo empleados activos
    return db.query(models.Employee).filter(models.Employee.is_active == True).all()

@router.get("/{employee_id}", response_model=schemas.EmployeeResponse)
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return employee

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_employee(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    # Soft delete (solo desactivar)
    employee.is_active = False
    db.commit()
    return None