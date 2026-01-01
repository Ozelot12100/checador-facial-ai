import numpy as np
import face_recognition
from sqlalchemy.orm import Session
from models import Employee
from typing import Optional

class BiometricService:
    def __init__(self, db: Session):
        self.db = db
        self.threshold = 0.5 # Bajamos un poco el umbral para ser más estrictos con fotos reales

    def find_best_match(self, incoming_vector: list[float]) -> Optional[Employee]:
        # (Este método queda IGUAL que antes, no lo borres)
        if not incoming_vector:
            return None
        
        incoming_arr = np.array(incoming_vector)
        active_employees = self.db.query(Employee).filter(Employee.is_active == True).all()

        best_match = None
        min_distance = float('inf')

        for employee in active_employees:
            try:
                stored_vector = employee.face_vector
                if len(stored_vector) != len(incoming_vector):
                    continue
                
                stored_arr = np.array(stored_vector)
                distance = np.linalg.norm(incoming_arr - stored_arr)

                if distance < min_distance:
                    min_distance = distance
                    best_match = employee
            except Exception:
                continue

        if min_distance < self.threshold:
            return best_match
        
        return None

    # --- NUEVA FUNCIÓN DE IA ---
    @staticmethod
    def vector_from_image(file_bytes) -> Optional[list[float]]:
        """
        Recibe los bytes de una imagen, detecta la cara y retorna el vector (encoding).
        Retorna None si no encuentra ninguna cara.
        """
        try:
            # Cargar imagen desde bytes
            image = face_recognition.load_image_file(file_bytes)
            
            # Detectar caras y generar encodings (vectores)
            # num_jitters=1 hace que sea rápido. Aumentar para más precisión.
            encodings = face_recognition.face_encodings(image)

            if len(encodings) > 0:
                # Retornamos el de la primera cara encontrada y lo convertimos a lista normal
                return encodings[0].tolist()
            
            return None
        except Exception as e:
            print(f"Error procesando imagen: {e}")
            return None

    @staticmethod
    def calculate_distance(vec1: list[float], vec2: list[float]) -> float:
        return float(np.linalg.norm(np.array(vec1) - np.array(vec2)))