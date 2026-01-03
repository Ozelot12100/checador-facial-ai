import uuid
import json
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Función para generar IDs únicos (Guid en C#)
def generate_uuid():
    return str(uuid.uuid4())

class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, default=generate_uuid)
    code = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    
    # En base de datos se guarda como texto plano: "[0.12, -0.5, ...]"
    face_vector_json = Column(String, default="[]")
    photo_path = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime, nullable=True)  # Fecha de desactivación para auditoría
    created_at_utc = Column(DateTime, default=datetime.utcnow)

    # Relación con registros de asistencia
    attendance_records = relationship("AttendanceRecord", back_populates="employee")

    # Propiedad mágica para usar 'face_vector' como lista en Python
    # automáticamente convierte a/desde JSON al leer/escribir
    @property
    def face_vector(self):
        if not self.face_vector_json:
            return []
        return json.loads(self.face_vector_json)

    @face_vector.setter
    def face_vector(self, value):
        self.face_vector_json = json.dumps(value)


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.id"))
    
    timestamp_utc = Column(DateTime, default=datetime.utcnow)
    local_time = Column(DateTime, default=datetime.now)
    
    # 0 = CheckIn, 1 = CheckOut (Mismo enum que en C#)
    type = Column(Integer, nullable=False)
    
    # Puntuación de coincidencia (distancia) para auditoría
    match_score = Column(Float, nullable=False)
    photo_path = Column(String, nullable=True) # Ej: "uploads/abc-123.jpg"

    employee = relationship("Employee", back_populates="attendance_records")
    