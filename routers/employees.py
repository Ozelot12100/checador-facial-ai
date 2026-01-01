from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import database
import models
import schemas
from services.biometric import BiometricService

router = APIRouter(prefix="/api/employees", tags=["Employees"])
get_db = database.get_db

# NOTA: Usamos Form(...) y File(...) en lugar de un esquema JSON Pydantic
@router.post("/", response_model=schemas.EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_employee(
    code: str = Form(...),
    full_name: str = Form(...),
    file: UploadFile = File(...), # La foto es obligatoria
    db: Session = Depends(get_db)
):
    # 1. Procesar la imagen con IA para obtener el vector
    # file.file es el objeto binario que espera face_recognition
    face_vector = BiometricService.vector_from_image(file.file)

    if not face_vector:
        raise HTTPException(
            status_code=400, 
            detail="No se detectó ningún rostro en la imagen. Intente con una foto más clara."
        )

    # 2. Verificar duplicados por código
    existing_employee = db.query(models.Employee).filter(models.Employee.code == code).first()
    
    if existing_employee:
        # Actualización
        existing_employee.full_name = full_name
        existing_employee.face_vector = face_vector
        existing_employee.is_active = True
        db.commit()
        db.refresh(existing_employee)
        return existing_employee

    # 3. Creación
    new_employee = models.Employee(
        code=code,
        full_name=full_name,
        face_vector=face_vector
    )
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return new_employee

# Los demás endpoints (GET, DELETE) quedan igual que antes...
@router.get("/", response_model=List[schemas.EmployeeResponse])
def get_all_employees(db: Session = Depends(get_db)):
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
    employee.is_active = False
    db.commit()
    return None