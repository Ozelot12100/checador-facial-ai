import requests
import os

# Configuración
BASE_URL = "http://localhost:8000/api"
FOTO_REGISTRO = "foto_registro.jpg"
FOTO_ASISTENCIA = "foto_asistencia.jpg"

def verificar_archivos():
    if not os.path.exists(FOTO_REGISTRO) or not os.path.exists(FOTO_ASISTENCIA):
        print("? ERROR: Faltan las imágenes de prueba.")
        print(f"Por favor coloca '{FOTO_REGISTRO}' y '{FOTO_ASISTENCIA}' en esta carpeta.")
        return False
    return True

def run_test():
    print("--- ? INICIANDO PRUEBA DE RECONOCIMIENTO FACIAL ---")
    
    if not verificar_archivos():
        return

    # 1. Registrar Empleado con Foto
    print(f"\n1. ? Subiendo '{FOTO_REGISTRO}' para registrar empleado...")
    
    with open(FOTO_REGISTRO, "rb") as f:
        files = {"file": f}
        data = {
            "code": "EMP-IA-001", 
            "full_name": "Ingeniero de Prueba"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/employees/", files=files, data=data)
            
            if response.status_code == 201:
                print("? Empleado registrado exitosamente.")
                print(f"   ID: {response.json()['id']}")
            elif response.status_code == 409:
                print("? El empleado ya existía, continuamos...")
            else:
                print(f"? Error: {response.text}")
                return
        except Exception as e:
            print(f"? Error de conexión: {e}")
            return

    # 2. Check-in con Foto (Entrada)
    print(f"\n2. ? Enviando '{FOTO_ASISTENCIA}' para Check-in...")
    
    with open(FOTO_ASISTENCIA, "rb") as f:
        files = {"file": f}
        
        response = requests.post(f"{BASE_URL}/attendance/check-in", files=files)
        
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json['success']:
                print(f"? RECONOCIDO: {resp_json['message']}")
                print(f"   Empleado: {resp_json['employee_name']}")
                print(f"   Hora: {resp_json['time']}")
            else:
                print(f"? NO RECONOCIDO: {resp_json['message']}")
        else:
            print(f"? Error en petición: {response.text}")

    print("\n--- FIN DE LA PRUEBA ---")

if __name__ == "__main__":
    run_test()